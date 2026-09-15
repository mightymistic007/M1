import unittest
import time
import numpy as np
from models.m4_optimization_solver import M4OptimizationSolver

class TestM4SolverPerformance(unittest.TestCase):
    def setUp(self):
        self.solver = M4OptimizationSolver()

    def _generate_synthetic_batch(self, n_records: int):
        np.random.seed(42)
        values = np.random.uniform(50.0, 350.0, n_records)
        delays = np.random.randint(0, 6, n_records)
        risks = np.random.uniform(0.1, 0.95, n_records)

        return [
            {
                "shipment_id": f"PERF-{i:05d}",
                "order_value_usd": float(round(values[i], 2)),
                "estimated_delay_days": int(delays[i]),
                "predicted_delay_risk": float(round(risks[i], 4))
            }
            for i in range(n_records)
        ]

    def test_latency_small_batch_n10(self):
        """Standard micro-batch (N=10) should execute under 25ms."""
        batch = self._generate_synthetic_batch(10)
        start = time.perf_counter()
        results = self.solver.solve_batch(batch)
        elapsed_ms = (time.perf_counter() - start) * 1000

        self.assertEqual(len(results), 10)
        self.assertLess(elapsed_ms, 25.0)

    def test_latency_medium_batch_n100(self):
        """Standard operational batch (N=100) should execute under 100ms."""
        batch = self._generate_synthetic_batch(100)
        start = time.perf_counter()
        results = self.solver.solve_batch(batch)
        elapsed_ms = (time.perf_counter() - start) * 1000

        self.assertEqual(len(results), 100)
        self.assertLess(elapsed_ms, 100.0)

    def test_throughput_stress_n500(self):
        """Stress batch (N=500) must execute within 500ms without memory degradation."""
        batch = self._generate_synthetic_batch(500)
        start = time.perf_counter()
        results = self.solver.solve_batch(batch)
        elapsed_ms = (time.perf_counter() - start) * 1000

        self.assertEqual(len(results), 500)
        self.assertLess(elapsed_ms, 500.0)

if __name__ == "__main__":
    unittest.main()