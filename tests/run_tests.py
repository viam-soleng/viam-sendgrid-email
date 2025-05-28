#!/usr/bin/env python3
import unittest
import sys
from pathlib import Path

from tests.test_sendgrid_email import (
    TestInitialization,
    TestValidateMissingApiKey,
    TestValidateEnforcePresetNoMessages,
    TestSendBasicEmail,
    TestSendWithAttachment,
    TestSendWithPreset,
    TestSendMissingTo,
    TestSendApiFailure
)

def create_test_suite():
    """Create a test suite with all tests."""
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTests(loader.loadTestsFromTestCase(TestInitialization))
    test_suite.addTests(loader.loadTestsFromTestCase(TestValidateMissingApiKey))
    test_suite.addTests(loader.loadTestsFromTestCase(TestValidateEnforcePresetNoMessages))
    test_suite.addTests(loader.loadTestsFromTestCase(TestSendBasicEmail))
    test_suite.addTests(loader.loadTestsFromTestCase(TestSendWithAttachment))
    test_suite.addTests(loader.loadTestsFromTestCase(TestSendWithPreset))
    test_suite.addTests(loader.loadTestsFromTestCase(TestSendMissingTo))
    test_suite.addTests(loader.loadTestsFromTestCase(TestSendApiFailure))

    return test_suite

if __name__ == '__main__':
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())