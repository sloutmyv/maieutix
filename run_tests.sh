#!/bin/bash

# Script pour exécuter les tests de ConsultationPreparationNaissance

echo "=== Exécution des tests de ConsultationPreparationNaissance ==="

echo "1. Tests de modèles..."
docker-compose exec web python manage.py test core.tests.models.test_consultation_preparation_naissance -v 2

echo -e "\n2. Tests de formulaires..."
docker-compose exec web python manage.py test core.tests.forms.test_consultation_preparation_naissance_forms -v 2

echo -e "\n3. Tests de vues..."
docker-compose exec web python manage.py test core.tests.views.test_consultation_preparation_naissance_views -v 2

echo -e "\n4. Tests d'admin..."
docker-compose exec web python manage.py test core.tests.admin.test_consultation_preparation_naissance_admin -v 2

echo -e "\n5. Tests d'intégration..."
docker-compose exec web python manage.py test core.tests.integration.test_consultation_preparation_naissance_integration -v 2

echo -e "\n=== Tests terminés ==="