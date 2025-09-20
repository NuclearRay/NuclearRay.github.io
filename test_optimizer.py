"""
Test suite for the Game Currency Optimizer

This module contains comprehensive tests for the dynamic programming
currency optimization algorithms.
"""

import unittest
from currency_optimizer import CurrencyOptimizer, CurrencyPackage, create_common_packages


class TestCurrencyOptimizer(unittest.TestCase):
    """Test cases for the CurrencyOptimizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Simple test packages
        self.simple_packages = [
            CurrencyPackage(1.0, 100, "Small"),
            CurrencyPackage(5.0, 600, "Medium"),
            CurrencyPackage(10.0, 1300, "Large")
        ]
        
        # Real-world packages
        self.real_packages = create_common_packages()
        
        self.simple_optimizer = CurrencyOptimizer(self.simple_packages)
        self.real_optimizer = CurrencyOptimizer(self.real_packages)
    
    def test_package_creation(self):
        """Test CurrencyPackage creation and properties."""
        package = CurrencyPackage(9.99, 1000, "Test Package")
        
        self.assertEqual(package.cost, 9.99)
        self.assertEqual(package.currency_amount, 1000)
        self.assertEqual(package.name, "Test Package")
        self.assertAlmostEqual(package.efficiency, 1000 / 9.99, places=2)
    
    def test_zero_target(self):
        """Test optimization with zero target currency."""
        cost, solution = self.simple_optimizer.find_optimal_purchase_unbounded(0)
        
        self.assertEqual(cost, 0.0)
        self.assertEqual(len(solution), 0)
    
    def test_simple_optimization(self):
        """Test optimization with simple packages."""
        # Test case where exact match is possible
        cost, solution = self.simple_optimizer.find_optimal_purchase_unbounded(100)
        
        self.assertEqual(cost, 1.0)  # Should buy 1x Small package
        self.assertEqual(len(solution), 1)
        
        # Test case requiring combination
        cost, solution = self.simple_optimizer.find_optimal_purchase_unbounded(700)
        
        # Should be 1x Medium (600) + 1x Small (100) = 700 coins for $6
        self.assertEqual(cost, 6.0)
        self.assertEqual(len(solution), 2)
    
    def test_efficiency_calculation(self):
        """Test package efficiency calculations."""
        analysis = self.simple_optimizer.analyze_packages()
        
        # Packages should be sorted by efficiency (descending)
        efficiencies = [pkg['efficiency'] for pkg in analysis]
        self.assertEqual(efficiencies, sorted(efficiencies, reverse=True))
        
        # Check specific efficiency values
        large_pkg = next(pkg for pkg in analysis if pkg['name'] == 'Large')
        self.assertAlmostEqual(large_pkg['efficiency'], 1300 / 10.0, places=2)
    
    def test_real_world_scenarios(self):
        """Test with realistic game currency packages."""
        test_cases = [
            (500, "Small purchase"),
            (1000, "Medium purchase"),
            (5000, "Large purchase"),
            (15000, "Bulk purchase")
        ]
        
        for target, description in test_cases:
            with self.subTest(target=target, description=description):
                cost, solution = self.real_optimizer.find_optimal_purchase_unbounded(target)
                
                # Verify solution is valid
                self.assertGreater(cost, 0, f"Cost should be positive for {description}")
                self.assertGreater(len(solution), 0, f"Solution should not be empty for {description}")
                
                # Verify we get at least the target currency
                total_currency = sum(pkg.currency_amount * qty for pkg, qty in solution.items())
                self.assertGreaterEqual(total_currency, target, 
                                      f"Should get at least {target} currency for {description}")
                
                # Verify cost calculation
                calculated_cost = sum(pkg.cost * qty for pkg, qty in solution.items())
                self.assertAlmostEqual(cost, calculated_cost, places=2,
                                     msg=f"Cost calculation mismatch for {description}")
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Very small target
        cost, solution = self.simple_optimizer.find_optimal_purchase_unbounded(1)
        self.assertGreater(cost, 0)
        
        # Target exactly matching a package
        cost, solution = self.simple_optimizer.find_optimal_purchase_unbounded(600)
        self.assertEqual(cost, 5.0)  # Should buy exactly 1x Medium
        
        # Target requiring multiple of same package
        cost, solution = self.simple_optimizer.find_optimal_purchase_unbounded(1200)
        # Should buy 2x Medium packages (1200 coins for $10)
        self.assertEqual(cost, 10.0)
    
    def test_package_sorting(self):
        """Test that packages are sorted by efficiency."""
        optimizer = CurrencyOptimizer(self.simple_packages)
        
        # Check that packages are sorted by efficiency (descending)
        for i in range(len(optimizer.packages) - 1):
            self.assertGreaterEqual(optimizer.packages[i].efficiency, 
                                  optimizer.packages[i + 1].efficiency)
    
    def test_large_targets(self):
        """Test optimization with large target values."""
        large_targets = [50000, 100000]
        
        for target in large_targets:
            with self.subTest(target=target):
                cost, solution = self.real_optimizer.find_optimal_purchase_unbounded(target)
                
                self.assertGreater(cost, 0)
                self.assertGreater(len(solution), 0)
                
                # Verify we get at least the target
                total_currency = sum(pkg.currency_amount * qty for pkg, qty in solution.items())
                self.assertGreaterEqual(total_currency, target)
    
    def test_single_package_scenarios(self):
        """Test scenarios with single package types."""
        single_package = [CurrencyPackage(10.0, 1000, "Only Package")]
        optimizer = CurrencyOptimizer(single_package)
        
        # Test various targets
        test_targets = [500, 1000, 1500, 2000]
        
        for target in test_targets:
            with self.subTest(target=target):
                cost, solution = optimizer.find_optimal_purchase_unbounded(target)
                
                # Should only use the single package
                self.assertEqual(len(solution), 1)
                
                package, quantity = next(iter(solution.items()))
                expected_quantity = (target + package.currency_amount - 1) // package.currency_amount
                self.assertEqual(quantity, expected_quantity)


class TestPerformance(unittest.TestCase):
    """Performance tests for the optimizer."""
    
    def setUp(self):
        """Set up performance test fixtures."""
        # Create many packages for performance testing
        self.many_packages = []
        for i in range(20):
            cost = 1.0 + i * 0.5
            currency = 100 + i * 50
            self.many_packages.append(CurrencyPackage(cost, currency, f"Package_{i}"))
        
        self.performance_optimizer = CurrencyOptimizer(self.many_packages)
    
    def test_performance_with_many_packages(self):
        """Test performance with many package options."""
        import time
        
        targets = [1000, 5000, 10000]
        
        for target in targets:
            with self.subTest(target=target):
                start_time = time.time()
                cost, solution = self.performance_optimizer.find_optimal_purchase_unbounded(target)
                end_time = time.time()
                
                # Should complete within reasonable time (less than 1 second)
                self.assertLess(end_time - start_time, 1.0, 
                              f"Optimization took too long for target {target}")
                
                # Verify solution is valid
                self.assertGreater(cost, 0)
                total_currency = sum(pkg.currency_amount * qty for pkg, qty in solution.items())
                self.assertGreaterEqual(total_currency, target)


def run_comprehensive_tests():
    """Run all tests and provide detailed output."""
    print("=== Running Comprehensive Tests ===\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCurrencyOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    
    if success:
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[FAILED] Some tests failed!")
        exit(1)
