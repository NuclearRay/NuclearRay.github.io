"""
Demo script showing the Game Currency Optimizer in action

This script demonstrates various features of the optimizer with
clear examples and explanations.
"""

from currency_optimizer import CurrencyOptimizer, CurrencyPackage, create_common_packages


def demo_basic_optimization():
    """Demonstrate basic optimization functionality."""
    print("=== BASIC OPTIMIZATION DEMO ===\n")
    
    # Create some example packages (typical mobile game pricing)
    packages = [
        CurrencyPackage(0.99, 100, "Starter Pack"),
        CurrencyPackage(4.99, 600, "Value Pack"),
        CurrencyPackage(9.99, 1300, "Popular Pack"),
        CurrencyPackage(19.99, 2800, "Great Deal"),
        CurrencyPackage(49.99, 7500, "Best Value"),
        CurrencyPackage(99.99, 16000, "Ultimate Pack")
    ]
    
    optimizer = CurrencyOptimizer(packages)
    
    print("Available Packages:")
    for pkg in packages:
        print(f"  {pkg.name}: ${pkg.cost:.2f} for {pkg.currency_amount} coins ({pkg.efficiency:.1f} coins/$)")
    
    print("\n" + "="*60 + "\n")
    
    # Test different scenarios
    scenarios = [
        (500, "Small purchase - need 500 coins"),
        (2000, "Medium purchase - need 2000 coins"),
        (5000, "Large purchase - need 5000 coins"),
        (12000, "Bulk purchase - need 12000 coins")
    ]
    
    for target, description in scenarios:
        print(f"SCENARIO: {description}")
        print(f"Target: {target} coins")
        
        cost, solution = optimizer.find_optimal_purchase_unbounded(target)
        
        print(f"Optimal cost: ${cost:.2f}")
        print("Purchase plan:")
        
        total_currency = 0
        for package, quantity in solution.items():
            total_currency += package.currency_amount * quantity
            print(f"  {quantity}x {package.name} = ${package.cost * quantity:.2f} ({package.currency_amount * quantity} coins)")
        
        print(f"Total currency obtained: {total_currency} coins")
        print(f"Efficiency: {total_currency / cost:.2f} coins/$")
        print(f"Overpurchase: {total_currency - target} coins ({((total_currency - target) / target * 100):.1f}%)")
        print()


def demo_strategy_comparison():
    """Demonstrate comparison between different strategies."""
    print("=== STRATEGY COMPARISON DEMO ===\n")
    
    packages = create_common_packages()
    optimizer = CurrencyOptimizer(packages)
    
    target = 3000
    print(f"Comparing strategies for {target} coins:\n")
    
    # Optimal strategy
    optimal_cost, optimal_solution = optimizer.find_optimal_purchase_unbounded(target)
    
    # Greedy strategy (always buy most efficient)
    most_efficient = max(packages, key=lambda p: p.efficiency)
    greedy_quantity = (target + most_efficient.currency_amount - 1) // most_efficient.currency_amount
    greedy_cost = greedy_quantity * most_efficient.cost
    greedy_currency = greedy_quantity * most_efficient.currency_amount
    
    # Single largest package strategy
    largest_package = max(packages, key=lambda p: p.currency_amount)
    large_quantity = (target + largest_package.currency_amount - 1) // largest_package.currency_amount
    large_cost = large_quantity * largest_package.cost
    large_currency = large_quantity * largest_package.currency_amount
    
    print("1. OPTIMAL STRATEGY (Dynamic Programming):")
    print(f"   Cost: ${optimal_cost:.2f}")
    total_optimal = sum(pkg.currency_amount * qty for pkg, qty in optimal_solution.items())
    print(f"   Currency: {total_optimal} coins")
    print(f"   Efficiency: {total_optimal / optimal_cost:.2f} coins/$")
    for package, quantity in optimal_solution.items():
        print(f"   {quantity}x {package.name}")
    
    print(f"\n2. GREEDY STRATEGY (Most efficient package only):")
    print(f"   Cost: ${greedy_cost:.2f}")
    print(f"   Currency: {greedy_currency} coins")
    print(f"   Efficiency: {greedy_currency / greedy_cost:.2f} coins/$")
    print(f"   {greedy_quantity}x {most_efficient.name}")
    
    print(f"\n3. LARGEST PACKAGE STRATEGY:")
    print(f"   Cost: ${large_cost:.2f}")
    print(f"   Currency: {large_currency} coins")
    print(f"   Efficiency: {large_currency / large_cost:.2f} coins/$")
    print(f"   {large_quantity}x {largest_package.name}")
    
    print(f"\nSAVINGS with optimal strategy:")
    print(f"   vs Greedy: ${greedy_cost - optimal_cost:.2f} ({((greedy_cost - optimal_cost) / optimal_cost * 100):.1f}%)")
    print(f"   vs Largest: ${large_cost - optimal_cost:.2f} ({((large_cost - optimal_cost) / optimal_cost * 100):.1f}%)")


def demo_custom_packages():
    """Demonstrate with custom game packages."""
    print("\n=== CUSTOM PACKAGES DEMO ===\n")
    
    # Example: RPG game with different currency types
    custom_packages = [
        CurrencyPackage(1.99, 200, "Adventurer's Pouch"),
        CurrencyPackage(3.99, 450, "Merchant's Bundle"),
        CurrencyPackage(7.99, 1000, "Hero's Treasure"),
        CurrencyPackage(15.99, 2200, "Dragon's Hoard"),
        CurrencyPackage(29.99, 4500, "King's Vault"),
        CurrencyPackage(59.99, 10000, "Legendary Chest")
    ]
    
    optimizer = CurrencyOptimizer(custom_packages)
    
    print("Custom RPG Currency Packages:")
    analysis = optimizer.analyze_packages()
    for pkg in analysis:
        print(f"  {pkg['name']}: ${pkg['cost']:.2f} for {pkg['currency']} gold ({pkg['efficiency']:.1f} gold/$)")
    
    print(f"\nOptimizing for 6000 gold coins:")
    cost, solution = optimizer.find_optimal_purchase_unbounded(6000)
    
    print(f"Optimal cost: ${cost:.2f}")
    total_currency = 0
    for package, quantity in solution.items():
        total_currency += package.currency_amount * quantity
        print(f"  {quantity}x {package.name} = ${package.cost * quantity:.2f}")
    
    print(f"Total gold obtained: {total_currency}")
    print(f"Efficiency: {total_currency / cost:.2f} gold/$")


def demo_efficiency_analysis():
    """Demonstrate package efficiency analysis."""
    print("\n=== EFFICIENCY ANALYSIS DEMO ===\n")
    
    packages = create_common_packages()
    optimizer = CurrencyOptimizer(packages)
    
    analysis = optimizer.analyze_packages()
    
    print("Package Efficiency Analysis:")
    print("-" * 70)
    print(f"{'Package':<15} {'Cost':<8} {'Currency':<10} {'Efficiency':<12} {'$/Coin':<8}")
    print("-" * 70)
    
    for pkg in analysis:
        print(f"{pkg['name']:<15} ${pkg['cost']:<7.2f} {pkg['currency']:<10} "
              f"{pkg['efficiency']:<12.2f} ${pkg['cost_per_coin']:<7.4f}")
    
    print(f"\nKey Insights:")
    best_efficiency = analysis[0]
    worst_efficiency = analysis[-1]
    
    print(f"• Most efficient: {best_efficiency['name']} ({best_efficiency['efficiency']:.1f} coins/$)")
    print(f"• Least efficient: {worst_efficiency['name']} ({worst_efficiency['efficiency']:.1f} coins/$)")
    print(f"• Efficiency range: {best_efficiency['efficiency'] / worst_efficiency['efficiency']:.1f}x difference")
    
    # Find break-even point
    mid_range_target = 5000
    cost, solution = optimizer.find_optimal_purchase_unbounded(mid_range_target)
    packages_used = len([pkg for pkg, qty in solution.items() if qty > 0])
    
    print(f"• For {mid_range_target} coins, optimal solution uses {packages_used} different package types")


if __name__ == "__main__":
    print("=== GAME CURRENCY OPTIMIZER DEMONSTRATION ===\n")
    print("This demo shows how dynamic programming can optimize")
    print("your game currency purchases for maximum value!\n")
    
    demo_basic_optimization()
    demo_strategy_comparison()
    demo_custom_packages()
    demo_efficiency_analysis()
    
    print("\n" + "="*60)
    print("Demo complete! Try running 'python interactive_optimizer.py'")
    print("for an interactive experience with visualization features.")
    print("="*60)
