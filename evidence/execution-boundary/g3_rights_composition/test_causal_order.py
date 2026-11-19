import unittest

from g3_rights_composition.causal_order import check_authorization_order


class CausalAuthorizationOrderTests(unittest.TestCase):
    def check(self, *edges, withdrawals=("withdraw",)):
        return check_authorization_order(
            ("grant", "commit", "withdraw", "witness"), edges,
            grant="grant", commit="commit", withdrawals=withdrawals,
        )

    def test_order_can_be_forced_by_a_causal_chain(self):
        result = self.check(("grant", "commit"), ("commit", "witness"), ("witness", "withdraw"))
        self.assertEqual(result["verdict"], "forced")
        self.assertIsNone(result["opposing_order"])

    def test_same_events_with_an_unordered_withdrawal_admit_both_verdicts(self):
        result = self.check(("grant", "commit"), ("grant", "withdraw"))
        self.assertEqual(result["verdict"], "ambiguous")
        supporting, opposing = result["supporting_order"], result["opposing_order"]
        self.assertLess(supporting.index("commit"), supporting.index("withdraw"))
        self.assertLess(opposing.index("withdraw"), opposing.index("commit"))

    def test_early_withdrawal_excludes_authorization(self):
        result = self.check(("grant", "withdraw"), ("withdraw", "commit"))
        self.assertEqual(result["verdict"], "excluded")
        self.assertIsNone(result["supporting_order"])

    def test_missing_scope_differs_from_empty_withdrawal_inventory(self):
        edges = (("grant", "commit"),)
        self.assertEqual(self.check(*edges, withdrawals=None)["verdict"], "incomplete_scope")
        self.assertEqual(self.check(*edges, withdrawals=())["verdict"], "forced")

    def test_cycles_and_unknown_events_reject(self):
        with self.assertRaises(ValueError):
            self.check(("grant", "commit"), ("commit", "grant"))
        with self.assertRaises(ValueError):
            self.check(("missing", "commit"))
        with self.assertRaises(ValueError):
            self.check("xy")


if __name__ == "__main__":
    unittest.main()
