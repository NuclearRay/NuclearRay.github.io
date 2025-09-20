"""
Interactive Game Currency Optimizer with Visualization

This module provides an interactive interface for optimizing game currency purchases
with visualization capabilities and advanced analysis features.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple
from currency_optimizer import CurrencyOptimizer, CurrencyPackage, create_common_packages


class InteractiveCurrencyOptimizer:
    """Enhanced optimizer with visualization and interactive features."""
    
    def __init__(self, packages: List[CurrencyPackage]):
        self.optimizer = CurrencyOptimizer(packages)
        self.packages = packages
    
    def plot_efficiency_analysis(self):
        """Plot efficiency analysis of all packages."""
        analysis = self.optimizer.analyze_packages()
        
        names = [pkg['name'] for pkg in analysis]
        efficiencies = [pkg['efficiency'] for pkg in analysis]
        costs = [pkg['cost'] for pkg in analysis]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Efficiency bar chart
        bars1 = ax1.bar(range(len(names)), efficiencies, color='skyblue', alpha=0.7)
        ax1.set_xlabel('Packages')
        ax1.set_ylabel('Coins per Dollar')
        ax1.set_title('Package Efficiency (Coins per Dollar)')
        ax1.set_xticks(range(len(names)))
        ax1.set_xticklabels(names, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, eff in zip(bars1, efficiencies):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{eff:.1f}', ha='center', va='bottom')
        
        # Cost vs Currency scatter plot
        currencies = [pkg['currency'] for pkg in analysis]
        scatter = ax2.scatter(costs, currencies, c=efficiencies, cmap='viridis', 
                            s=100, alpha=0.7, edgecolors='black')
        ax2.set_xlabel('Cost ($)')
        ax2.set_ylabel('Currency Amount')
        ax2.set_title('Cost vs Currency (Color = Efficiency)')
        
        # Add package names as annotations
        for i, name in enumerate(names):
            ax2.annotate(name, (costs[i], currencies[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.colorbar(scatter, ax=ax2, label='Efficiency (coins/$)')
        plt.tight_layout()
        plt.show()
    
    def plot_optimization_curve(self, max_target: int = 10000, step: int = 100):
        """Plot the optimization curve showing cost vs target currency."""
        targets = list(range(step, max_target + 1, step))
        costs = []
        efficiencies = []
        
        print("Calculating optimization curve...")
        for target in targets:
            cost, _ = self.optimizer.find_optimal_purchase_unbounded(target)
            costs.append(cost)
            efficiencies.append(target / cost if cost > 0 else 0)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Cost curve
        ax1.plot(targets, costs, 'b-', linewidth=2, marker='o', markersize=3)
        ax1.set_xlabel('Target Currency')
        ax1.set_ylabel('Minimum Cost ($)')
        ax1.set_title('Optimal Cost vs Target Currency')
        ax1.grid(True, alpha=0.3)
        
        # Efficiency curve
        ax2.plot(targets, efficiencies, 'g-', linewidth=2, marker='s', markersize=3)
        ax2.set_xlabel('Target Currency')
        ax2.set_ylabel('Overall Efficiency (coins/$)')
        ax2.set_title('Overall Efficiency vs Target Currency')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def compare_strategies(self, target_currency: int):
        """Compare different purchasing strategies."""
        print(f"\n=== Strategy Comparison for {target_currency} coins ===\n")
        
        # Strategy 1: Optimal DP solution
        optimal_cost, optimal_solution = self.optimizer.find_optimal_purchase_unbounded(target_currency)
        
        # Strategy 2: Greedy (most efficient packages first)
        greedy_cost, greedy_solution = self._greedy_strategy(target_currency)
        
        # Strategy 3: Single package type (best efficiency)
        best_package = max(self.packages, key=lambda p: p.efficiency)
        single_quantity = (target_currency + best_package.currency_amount - 1) // best_package.currency_amount
        single_cost = single_quantity * best_package.cost
        single_currency = single_quantity * best_package.currency_amount
        
        print("1. OPTIMAL (Dynamic Programming):")
        print(f"   Cost: ${optimal_cost:.2f}")
        print(f"   Efficiency: {target_currency / optimal_cost:.2f} coins/$")
        for package, quantity in optimal_solution.items():
            print(f"   {quantity}x {package.name}")
        
        print("\n2. GREEDY (Most efficient first):")
        print(f"   Cost: ${greedy_cost:.2f}")
        print(f"   Efficiency: {target_currency / greedy_cost:.2f} coins/$")
        for package, quantity in greedy_solution.items():
            if quantity > 0:
                print(f"   {quantity}x {package.name}")
        
        print(f"\n3. SINGLE PACKAGE ({best_package.name}):")
        print(f"   Cost: ${single_cost:.2f}")
        print(f"   Currency obtained: {single_currency}")
        print(f"   Efficiency: {single_currency / single_cost:.2f} coins/$")
        
        # Calculate savings
        greedy_savings = ((greedy_cost - optimal_cost) / optimal_cost) * 100
        single_savings = ((single_cost - optimal_cost) / optimal_cost) * 100
        
        print(f"\nSAVINGS with optimal strategy:")
        print(f"   vs Greedy: ${greedy_cost - optimal_cost:.2f} ({greedy_savings:.1f}%)")
        print(f"   vs Single: ${single_cost - optimal_cost:.2f} ({single_savings:.1f}%)")
    
    def _greedy_strategy(self, target_currency: int) -> Tuple[float, Dict[CurrencyPackage, int]]:
        """Implement greedy strategy for comparison."""
        remaining = target_currency
        total_cost = 0.0
        solution = {pkg: 0 for pkg in self.packages}
        
        # Sort by efficiency (already done in optimizer)
        sorted_packages = sorted(self.packages, key=lambda p: p.efficiency, reverse=True)
        
        for package in sorted_packages:
            if remaining <= 0:
                break
            
            quantity = remaining // package.currency_amount
            if quantity > 0:
                solution[package] = quantity
                total_cost += quantity * package.cost
                remaining -= quantity * package.currency_amount
        
        # If we still need more currency, buy one more of the most efficient package
        if remaining > 0:
            best_package = sorted_packages[0]
            solution[best_package] += 1
            total_cost += best_package.cost
        
        return total_cost, solution
    
    def interactive_session(self):
        """Run an interactive optimization session."""
        print("=== Interactive Game Currency Optimizer ===\n")
        
        while True:
            print("\nOptions:")
            print("1. Optimize for target currency")
            print("2. Exact or scaled exact-match optimization (up to 100x)")
            print("3. Analyze packages")
            print("4. Compare strategies")
            print("5. Plot efficiency analysis")
            print("6. Plot optimization curve")
            print("7. Add custom package")
            print("8. Exit")
            print("9. Optimize spend given budget and item costs")
            
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == '1':
                try:
                    try:
                        target = int(eval(input("Enter target currency amount (e.g., 1000 or 10*100): ")))
                    except:
                        print("Invalid input. Please enter a valid integer or an expression that evaluates to an integer.")
                        continue
                    cost, solution = self.optimizer.find_optimal_purchase_unbounded(target)
                    
                    print(f"\nOptimal solution for {target} coins:")
                    print(f"Minimum cost: ${cost:.2f}")
                    print("Purchase plan:")
                    
                    total_currency = 0
                    for package, quantity in solution.items():
                        if quantity > 0:
                            total_currency += package.currency_amount * quantity
                            print(f"  {quantity}x {package.name} = ${package.cost * quantity:.2f}")
                    
                    print(f"Total currency: {total_currency} coins")
                    print(f"Efficiency: {total_currency / cost:.2f} coins/$")
                    
                except ValueError:
                    print("Please enter a valid number.")
            
            elif choice == '2':
                try:
                    target = int(input("Enter target currency to match exactly: "))
                    k, cost, solution = self.optimizer.find_exact_or_scaled(target, max_multiplier=100)
                    if k == 0 or cost is None:
                        print(f"\nNo exact solution found for {target} coins or any multiple up to 100x.")
                    else:
                        scaled_target = k * target
                        print(f"\nExact solution found for {scaled_target} coins (multiplier = {k}x of {target}).")
                        print(f"Minimum cost: ${cost:.2f}")
                        print("Purchase plan:")
                        total_currency = 0
                        for package, quantity in solution.items():
                            if quantity > 0:
                                total_currency += package.currency_amount * quantity
                                print(f"  {quantity}x {package.name} = ${package.cost * quantity:.2f}")
                        print(f"Total currency (exact): {total_currency} coins")
                        print(f"Efficiency: {total_currency / cost:.2f} coins/$")
                except ValueError:
                    print("Please enter a valid number.")
            
            elif choice == '3':
                analysis = self.optimizer.analyze_packages()
                print("\nPackage Analysis:")
                print("-" * 80)
                print(f"{'Package':<20} {'Cost':<8} {'Currency':<10} {'Efficiency':<12} {'$/Coin':<8}")
                print("-" * 80)
                for pkg in analysis:
                    print(f"{pkg['name']:<20} ${pkg['cost']:<7.2f} {pkg['currency']:<10} "
                          f"{pkg['efficiency']:<12.2f} ${pkg['cost_per_coin']:<7.4f}")
            
            elif choice == '4':
                try:
                    target = int(input("Enter target currency for comparison: "))
                    self.compare_strategies(target)
                except ValueError:
                    print("Please enter a valid number.")
            
            elif choice == '5':
                try:
                    self.plot_efficiency_analysis()
                except ImportError:
                    print("Matplotlib not available. Install with: pip install matplotlib")
            
            elif choice == '6':
                try:
                    max_target = int(input("Enter maximum target currency (default 10000): ") or "10000")
                    self.plot_optimization_curve(max_target)
                except (ValueError, ImportError) as e:
                    if isinstance(e, ImportError):
                        print("Matplotlib not available. Install with: pip install matplotlib")
                    else:
                        print("Please enter a valid number.")
            
            elif choice == '7':
                try:
                    name = input("Package name: ")
                    cost = float(input("Package cost ($): "))
                    currency = int(input("Currency amount: "))
                    
                    new_package = CurrencyPackage(cost, currency, name)
                    self.packages.append(new_package)
                    self.optimizer = CurrencyOptimizer(self.packages)
                    
                    print(f"Added package: {new_package}")
                    
                except ValueError:
                    print("Please enter valid values.")
            
            elif choice == '8':
                print("Thanks for using the Currency Optimizer!")
                break
            
            elif choice == '9':
                try:
                    budget = int(input("Enter available in-game currency (budget): ").strip())
                    raw_costs = input("Enter item costs (comma-separated, e.g., 75,120,200): ").strip()
                    costs = [int(x) for x in raw_costs.split(',') if x.strip()]
                    mode = input("Are items repeatable? (y/n) [y]: ").strip().lower() or 'y'
                    repeatable = mode.startswith('y')

                    if repeatable:
                        spent, counts = self.optimizer.optimize_spend_unbounded(budget, costs)
                    else:
                        spent, counts = self.optimizer.optimize_spend_01(budget, costs)

                    leftover = budget - spent
                    print("\n=== Spend Optimization Result ===")
                    print(f"Budget: {budget}")
                    print(f"Spent:  {spent}")
                    print(f"Leftover: {leftover}")
                    if counts:
                        print("Items purchased:")
                        for c in sorted(counts.keys(), reverse=True):
                            print(f"  cost {c}: x{counts[c]}")
                    else:
                        print("No items could be purchased with the given constraints.")
                except ValueError:
                    print("Please enter valid integers for budget and costs.")
            
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Ask user for package type
    while True:
        package_type = input("Choose package type (starter, mid_range, premium, league of legends): ")
        if package_type in ["starter", "mid_range", "premium", "league of legends"]:
            break
        else:
            print("Invalid package type. Please try again.")
    
    # Create optimizer with chosen packages
    packages = create_common_packages(package_type)
    interactive_optimizer = InteractiveCurrencyOptimizer(packages)
    
    # Run interactive session
    interactive_optimizer.interactive_session()
