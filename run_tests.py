#!/usr/bin/env python
"""
Script pour lancer tous les tests du projet Maieutix.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'maieutix.settings'
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Lancer tous les tests
    failures = test_runner.run_tests([
        'core.tests.models.test_sagefemme',
        'core.tests.models.test_periode_activite_complet', 
        'core.tests.views.test_administration',
        'core.tests.views.test_periode_apis',
        'core.tests.forms.test_sagefemme_form',
        'core.tests.integration.test_templates_integration'
    ])
    
    if failures:
        sys.exit(bool(failures))