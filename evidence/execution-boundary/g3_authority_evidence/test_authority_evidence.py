"""Adversarial tests for the non-authorizing signed record verifier."""
import copy
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from authority_evidence import DOMAIN, encode_claim, inspect_claim


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.issuer = Ed25519PrivateKey.generate()
        self.other = Ed25519PrivateKey.generate()
        self.claim = dict(domain=DOMAIN, issuer='operator', serial='event-1',
                          subject='student-1', action='publish-offline-html',
                          effect_digest='a'*64, scope='course-1', purpose='lesson',
                          not_before=20, not_after=30, revocation_generation=4)
        self.packet = self.sign(self.claim)
        self.kw = dict(public_keys={'operator': self.issuer.public_key()},
                       revoked_serials=set(), minimum_generation=4, now=25,
                       subject='student-1', action='publish-offline-html',
                       effect_digest='a'*64, scope='course-1', purpose='lesson')

    def sign(self, claim, key=None):
        return {'claim': copy.deepcopy(claim),
                'signature': (key or self.issuer).sign(encode_claim(claim)).hex()}

    def check(self, packet=None, **kwargs):
        inputs = dict(self.kw)
        inputs.update(kwargs)
        return inspect_claim(self.packet if packet is None else packet, **inputs)

    def test_valid_signature_is_not_effect_authority_or_consent(self):
        status = self.check()
        self.assertTrue(status['signature_valid_for_record'])
        self.assertFalse(status['authorizes_effect'])
        self.assertFalse(status['authentic_consent_proved'])
        self.assertFalse(status['original_six_x3_proved'])

    def test_forged_signature(self):
        self.assertEqual(self.check(self.sign(self.claim, self.other))['code'],
                         'invalid_signature')

    def test_changed_subject_rejected(self):
        tampered = copy.deepcopy(self.packet)
        tampered['claim']['subject'] = 'student-2'
        self.assertEqual(self.check(tampered)['code'], 'invalid_signature')
        self.assertEqual(self.check(self.sign(tampered['claim']))['code'],
                         'subject_action_or_scope_mismatch')

    def test_changed_action_scope_digest_and_purpose(self):
        for key, value in [('action','delete'), ('scope','other-course'),
                           ('effect_digest','b'*64), ('purpose','other')]:
            with self.subTest(key=key):
                changed = dict(self.claim, **{key:value})
                self.assertEqual(self.check(self.sign(changed))['code'],
                                 'subject_action_or_scope_mismatch')

    def test_expiry_and_future(self):
        self.assertEqual(self.check(now=30)['code'], 'expired_or_not_yet_valid')
        self.assertEqual(self.check(now=19)['code'], 'expired_or_not_yet_valid')

    def test_revocation_and_generation(self):
        self.assertEqual(self.check(revoked_serials={'event-1'})['code'],
                         'revoked_record')
        self.assertEqual(self.check(minimum_generation=5)['code'],
                         'stale_revocation_generation')

    def test_unknown_key_and_relabelled_issuer(self):
        self.assertEqual(self.check(public_keys={})['code'], 'untrusted_issuer')
        changed=dict(self.claim, issuer='other')
        self.assertEqual(self.check(self.sign(changed))['code'], 'untrusted_issuer')

    def test_invalid_schema_and_extra_fields(self):
        changed = dict(self.claim, claims_consent=True)
        self.assertEqual(self.check({'claim':changed,'signature':'0'*128})['code'],
                         'claim_invalid')
        self.assertEqual(self.check({'claim':self.claim})['code'],'packet_schema')

    def test_reject_malformed_signature_and_boolean_time(self):
        self.assertEqual(self.check({'claim':self.claim,'signature':'f'})['code'],
                         'signature_schema')
        self.assertEqual(self.check(now=True)['code'], 'trusted_inputs_invalid')
        changed = dict(self.claim, revocation_generation=True)
        self.assertEqual(self.check({'claim':changed,'signature':'0'*128})['code'],
                         'claim_invalid')

    def test_domain_separation(self):
        changed = dict(self.claim, domain='g3-consent-proof-v1')
        self.assertEqual(self.check({'claim':changed,'signature':'0'*128})['code'],
                         'claim_invalid')


if __name__ == '__main__':
    unittest.main()
