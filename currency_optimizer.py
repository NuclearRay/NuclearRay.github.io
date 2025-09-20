"""
Game Currency Optimizer using Dynamic Programming

This module provides optimal solutions for purchasing game currency
given different purchase packages with varying costs and currency amounts.
"""

from typing import List, Tuple, Dict, Optional
import math


class CurrencyPackage:
    """Represents a currency purchase package."""
    
    def __init__(self, cost: float, currency_amount: int, name: str = ""):
        self.cost = cost
        self.currency_amount = currency_amount
        self.name = name or f"${cost:.2f} for {currency_amount} coins"
        self.efficiency = currency_amount / cost  # coins per dollar
    
    def __repr__(self):
        return f"CurrencyPackage({self.name}, cost=${self.cost:.2f}, currency={self.currency_amount}, efficiency={self.efficiency:.2f})"


class CurrencyOptimizer:
    """Dynamic Programming solution for optimal game currency purchases."""
    
    def __init__(self, packages: List[CurrencyPackage]):
        self.packages = sorted(packages, key=lambda p: p.efficiency, reverse=True)
        self.memo = {}
    
    def find_optimal_purchase(self, target_currency: int) -> Tuple[float, List[Tuple[CurrencyPackage, int]]]:
        """
        Find the minimum cost to obtain at least target_currency amount.
        
        Returns:
            Tuple of (minimum_cost, list_of_(package, quantity)_pairs)
        """
        if target_currency <= 0:
            return 0.0, []
        
        # Clear memo for new calculation
        self.memo = {}
        
        # DP table: dp[i] = minimum cost to get exactly i currency
        # We'll use a large number to represent impossible states
        INF = float('inf')
        dp = [INF] * (target_currency + 1)
        parent = [None] * (target_currency + 1)  # To reconstruct solution
        
        dp[0] = 0.0
        
        # Fill the DP table
        for i in range(target_currency + 1):
            if dp[i] == INF:
                continue
                
            for package in self.packages:
                next_currency = min(i + package.currency_amount, target_currency)
                new_cost = dp[i] + package.cost
                
                if new_cost < dp[next_currency]:
                    dp[next_currency] = new_cost
                    parent[next_currency] = (i, package)
        
        # Find minimum cost for at least target_currency
        min_cost = dp[target_currency]
        
        # Reconstruct the solution
        solution = []
        current = target_currency
        
        while parent[current] is not None:
            prev_currency, package = parent[current]
            
            # Count how many times this package was used
            found = False
            for i, (existing_package, count) in enumerate(solution):
                if existing_package == package:
                    solution[i] = (existing_package, count + 1)
                    found = True
                    break
            
            if not found:
                solution.append((package, 1))
            
            current = prev_currency
        
        return min_cost, solution
    
    def find_optimal_purchase_unbounded(self, target_currency: int) -> Tuple[float, Dict[CurrencyPackage, int]]:
        """
        Find optimal purchase using unbounded knapsack approach.
        Each package can be purchased multiple times.
        
        Returns:
            Tuple of (minimum_cost, dictionary_of_package_counts)
        """
        if target_currency <= 0:
            return 0.0, {}
        
        # Find the minimum package size to extend our DP table if needed
        min_package_size = min(pkg.currency_amount for pkg in self.packages)
        
        # Extend target to ensure we can find a solution
        extended_target = target_currency + min_package_size
        
        # DP table for unbounded knapsack
        dp = [float('inf')] * (extended_target + 1)
        parent = [None] * (extended_target + 1)
        
        dp[0] = 0.0
        
        for currency in range(1, extended_target + 1):
            for package in self.packages:
                if package.currency_amount <= currency:
                    cost = dp[currency - package.currency_amount] + package.cost
                    if cost < dp[currency]:
                        dp[currency] = cost
                        parent[currency] = package
        
        # Find the minimum cost for at least target_currency
        min_cost = float('inf')
        best_currency = target_currency
        
        for currency in range(target_currency, extended_target + 1):
            if dp[currency] < min_cost:
                min_cost = dp[currency]
                best_currency = currency
        
        # Reconstruct solution
        solution = {}
        current = best_currency
        
        while current > 0 and parent[current] is not None:
            package = parent[current]
            solution[package] = solution.get(package, 0) + 1
            current -= package.currency_amount
        
        return min_cost, solution
    
    def analyze_packages(self) -> List[Dict]:
        """Analyze the efficiency of all packages."""
        analysis = []
        for package in self.packages:
            analysis.append({
                'name': package.name,
                'cost': package.cost,
                'currency': package.currency_amount,
                'efficiency': package.efficiency,
                'cost_per_coin': package.cost / package.currency_amount
            })
        return sorted(analysis, key=lambda x: x['efficiency'], reverse=True)
    
    def find_exact_purchase_unbounded(self, target_currency: int) -> Tuple[Optional[float], Dict[CurrencyPackage, int]]:
        """Find an exact match for target_currency if possible (unbounded knapsack exact sum).

        Returns (cost, solution_dict). If exact is impossible, returns (None, {}).
        """
        if target_currency <= 0:
            return 0.0, {}

        # DP for exact amounts only
        dp = [float('inf')] * (target_currency + 1)
        parent: List[Optional[CurrencyPackage]] = [None] * (target_currency + 1)

        dp[0] = 0.0

        for amount in range(1, target_currency + 1):
            for package in self.packages:
                if package.currency_amount <= amount:
                    prev = amount - package.currency_amount
                    cost = dp[prev] + package.cost
                    if cost < dp[amount]:
                        dp[amount] = cost
                        parent[amount] = package

        if math.isinf(dp[target_currency]):
            return None, {}

        # Reconstruct exact solution
        solution: Dict[CurrencyPackage, int] = {}
        current = target_currency
        while current > 0 and parent[current] is not None:
            pkg = parent[current]
            solution[pkg] = solution.get(pkg, 0) + 1
            current -= pkg.currency_amount

        if current != 0:
            # Safety check, though it shouldn't happen if dp[target] != inf
            return None, {}

        return dp[target_currency], solution

    def find_exact_or_scaled(self, target_currency: int, max_multiplier: int = 100) -> Tuple[int, Optional[float], Dict[CurrencyPackage, int]]:
        """Try to find an exact solution for target_currency. If not possible, try k*target
        for k in [2..max_multiplier] and return the first exact solution found.

        Returns (multiplier_k, cost, solution_dict).
        - If exact match for original target is found, multiplier_k == 1
        - If no exact match up to max_multiplier, returns (0, None, {})
        """
        # Try exact first
        cost, solution = self.find_exact_purchase_unbounded(target_currency)
        if cost is not None:
            return 1, cost, solution

        # Try scaled targets
        for k in range(2, max_multiplier + 1):
            scaled_target = k * target_currency
            cost_k, solution_k = self.find_exact_purchase_unbounded(scaled_target)
            if cost_k is not None:
                return k, cost_k, solution_k

        return 0, None, {}

    def find_break_even_points(self) -> List[Dict]:
        """Find break-even points where different packages become optimal."""
        break_points = []
        
        # Compare each pair of packages
        for i, pkg1 in enumerate(self.packages):
            for j, pkg2 in enumerate(self.packages[i+1:], i+1):
                # Find where pkg1 and pkg2 have same total cost
                # pkg1.cost * x = pkg2.cost * y and pkg1.currency * x = pkg2.currency * y
                if pkg1.currency_amount != pkg2.currency_amount:
                    # Solve for the currency amount where they're equivalent
                    lcm_currency = math.lcm(pkg1.currency_amount, pkg2.currency_amount)
                    pkg1_quantity = lcm_currency // pkg1.currency_amount
                    pkg2_quantity = lcm_currency // pkg2.currency_amount
                    
                    pkg1_total_cost = pkg1.cost * pkg1_quantity
                    pkg2_total_cost = pkg2.cost * pkg2_quantity
                    
                    break_points.append({
                        'currency_amount': lcm_currency,
                        'package1': pkg1.name,
                        'package1_cost': pkg1_total_cost,
                        'package1_quantity': pkg1_quantity,
                        'package2': pkg2.name,
                        'package2_cost': pkg2_total_cost,
                        'package2_quantity': pkg2_quantity,
                        'better_package': pkg1.name if pkg1_total_cost < pkg2_total_cost else pkg2.name
                    })
        
        return sorted(break_points, key=lambda x: x['currency_amount'])

    # ---------- Spend optimization (maximize usage of in-game currency) ----------
    def optimize_spend_unbounded(self, budget: int, purchase_costs: List[int]) -> Tuple[int, Dict[int, int]]:
        """Given a budget (in-game currency) and item costs (repeatable), use as much budget as possible.

        Returns (spent_amount, counts_by_cost). Uses unbounded knapsack with boolean reachability.
        """
        if budget <= 0 or not purchase_costs:
            return 0, {}

        costs = sorted(set(c for c in purchase_costs if c > 0))
        if not costs:
            return 0, {}

        reachable = [False] * (budget + 1)
        parent_cost: List[Optional[int]] = [None] * (budget + 1)
        reachable[0] = True

        for amount in range(1, budget + 1):
            for c in costs:
                if c <= amount and reachable[amount - c]:
                    reachable[amount] = True
                    parent_cost[amount] = c
                    break

        # Find max spend ≤ budget
        spent = budget
        while spent >= 0 and not reachable[spent]:
            spent -= 1

        if spent <= 0 and not reachable[spent]:
            return 0, {}

        # Reconstruct counts
        counts: Dict[int, int] = {}
        cur = spent
        while cur > 0:
            c = parent_cost[cur]
            if c is None:
                break
            counts[c] = counts.get(c, 0) + 1
            cur -= c

        return spent, counts

    def optimize_spend_01(self, budget: int, purchase_costs: List[int]) -> Tuple[int, Dict[int, int]]:
        """Given a budget and item costs (each purchasable at most once), maximize spend.

        Returns (spent_amount, counts_by_cost) where counts are 0 or 1 for each cost value.
        Uses 0/1 knapsack DP with reconstruction.
        """
        n = len(purchase_costs)
        if budget <= 0 or n == 0:
            return 0, {}

        costs = [c for c in purchase_costs if c > 0]
        n = len(costs)
        if n == 0:
            return 0, {}

        # dp[i][b] = whether we can reach b using first i items
        dp = [[False] * (budget + 1) for _ in range(n + 1)]
        dp[0][0] = True

        for i in range(1, n + 1):
            ci = costs[i - 1]
            for b in range(budget + 1):
                # not take
                if dp[i - 1][b]:
                    dp[i][b] = True
                # take if possible
                if b - ci >= 0 and dp[i - 1][b - ci]:
                    dp[i][b] = True

        # Find best spend
        spent = budget
        while spent >= 0 and not dp[n][spent]:
            spent -= 1

        if spent < 0:
            return 0, {}

        # Reconstruct
        counts: Dict[int, int] = {}
        b = spent
        for i in range(n, 0, -1):
            if dp[i - 1][b]:
                # item i-1 not taken
                continue
            ci = costs[i - 1]
            if b - ci >= 0 and dp[i - 1][b - ci]:
                counts[ci] = counts.get(ci, 0) + 1
                b -= ci

        return spent, counts


def create_common_packages(preset: Optional[str] = None) -> List[CurrencyPackage]:
    """Create game currency package examples.

    If preset is provided, choose among:
    - 'starter': small, early-game friendly
    - 'mid_range': typical mid-tier offers
    - 'premium': high-value larger bundles
    - 'league of legends': example themed set
    Default (None) returns a balanced common set.
    """
    if preset is None:
        return [
            CurrencyPackage(0.99, 100, "Starter Pack"),
            CurrencyPackage(4.99, 600, "Value Pack"),
            CurrencyPackage(9.99, 1300, "Popular Pack"),
            CurrencyPackage(19.99, 2800, "Great Deal"),
            CurrencyPackage(49.99, 7500, "Best Value"),
            CurrencyPackage(99.99, 16000, "Ultimate Pack"),
        ]

    preset = preset.lower().strip()
    if preset == 'starter':
        return [
            CurrencyPackage(0.99, 90, "Tiny Pouch"),
            CurrencyPackage(2.99, 300, "Small Pouch"),
            CurrencyPackage(5.99, 650, "Starter Bundle"),
        ]
    if preset == 'mid_range':
        return [
            CurrencyPackage(3.99, 420, "Scout Pack"),
            CurrencyPackage(7.99, 900, "Adventurer Pack"),
            CurrencyPackage(14.99, 1900, "Explorer Pack"),
            CurrencyPackage(24.99, 3300, "Champion Pack"),
        ]
    if preset == 'premium':
        return [
            CurrencyPackage(9.99, 1400, "Premium I"),
            CurrencyPackage(19.99, 3000, "Premium II"),
            CurrencyPackage(49.99, 8200, "Premium III"),
            CurrencyPackage(99.99, 17000, "Premium Ultimate"),
        ]
    if preset == 'league of legends':
        return [
            CurrencyPackage(4.99, 575, "Riot Point Small"),
            CurrencyPackage(10.99, 1380, "Riot Point Medium"),
            CurrencyPackage(21.99, 2800, "Riot Point Large"),
            CurrencyPackage(34.99, 4500, "Riot Point XL"),
            CurrencyPackage(49.99, 6500, "Riot Point Ultimate"),
            CurrencyPackage(99.99, 13500, "Riot Point Ultimate X"),
            CurrencyPackage(244.99, 33500, "Riot Point Ultimate XX"),
            CurrencyPackage(429.99, 60200, "Riot Point Ultimate XXX"),
        ]

    # Fallback to default if unknown preset
    return create_common_packages(None)


if __name__ == "__main__":
    # Example usage
    packages = create_common_packages("starter")
    optimizer = CurrencyOptimizer(packages)
    
    print("=== Game Currency Optimizer ===\n")
    
    # Analyze packages
    print("Package Analysis (sorted by efficiency):")
    analysis = optimizer.analyze_packages()
    for pkg in analysis:
        print(f"  {pkg['name']}: {pkg['efficiency']:.2f} coins/$, ${pkg['cost_per_coin']:.4f}/coin")
    
    print("\n" + "="*50 + "\n")
    
    # Test different target amounts
    test_amounts = [500, 1000, 2500, 5000, 10000]
    
    for target in test_amounts:
        print(f"Target: {target} coins")
        
        cost, solution = optimizer.find_optimal_purchase_unbounded(target)
        
        print(f"  Minimum cost: ${cost:.2f}")
        print("  Optimal purchase:")
        
        total_currency = 0
        for package, quantity in solution.items():
            total_currency += package.currency_amount * quantity
            print(f"    {quantity}x {package.name} = ${package.cost * quantity:.2f} ({package.currency_amount * quantity} coins)")
        
        print(f"  Total currency obtained: {total_currency} coins")
        print(f"  Efficiency: {total_currency / cost:.2f} coins/$")
        print()
