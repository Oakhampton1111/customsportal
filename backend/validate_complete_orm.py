#!/usr/bin/env python3
"""
Comprehensive ORM Validation Script for Customs Broker Portal

This script validates the complete ORM implementation, focusing on:
- Model imports and availability
- Model structure validation
- Relationship testing
- Helper method testing
- Database schema compliance
- Integration testing

Author: Customs Broker Portal Development Team
Created: 2025-01-27
"""

import sys
import os
import traceback
from typing import Dict, List, Any, Optional
from decimal import Decimal

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}")

def print_subheader(title: str) -> None:
    """Print a formatted subsection header."""
    print(f"\n{'-'*60}")
    print(f" {title}")
    print(f"{'-'*60}")

def print_test_result(test_name: str, passed: bool, details: str = "") -> None:
    """Print formatted test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status:8} | {test_name}")
    if details:
        print(f"         | {details}")

def print_summary(section: str, passed: int, total: int) -> None:
    """Print section summary."""
    percentage = (passed / total * 100) if total > 0 else 0
    print(f"\n{section} Summary: {passed}/{total} tests passed ({percentage:.1f}%)")

class ORMValidator:
    """Comprehensive ORM validation class."""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = {}
        
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """Run a single test and track results."""
        self.total_tests += 1
        try:
            result = test_func(*args, **kwargs)
            if result:
                self.passed_tests += 1
                print_test_result(test_name, True)
                return True
            else:
                self.failed_tests += 1
                print_test_result(test_name, False, "Test returned False")
                return False
        except Exception as e:
            self.failed_tests += 1
            print_test_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    def validate_import_and_availability(self) -> Dict[str, int]:
        """Test that all models can be imported and are available."""
        print_header("1. IMPORT AND MODEL AVAILABILITY TESTS")
        
        section_passed = 0
        section_total = 0
        
        # Test basic imports
        def test_basic_imports():
            try:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                
                from models import (
                    TariffCode, TariffSection, TariffChapter, TradeAgreement,
                    DutyRate, FtaRate, DumpingDuty, Tco, GstProvision,
                    ExportCode, ProductClassification
                )
                return True
            except ImportError as e:
                print(f"Import error: {e}")
                return False
        
        section_total += 1
        if self.run_test("Import all models from models package", test_basic_imports):
            section_passed += 1
        
        # Test individual model availability
        def test_model_availability(model_name: str):
            try:
                from models import __all__
                return model_name in __all__
            except Exception:
                return False
        
        models_to_test = [
            "TariffCode", "ExportCode", "ProductClassification",
            "TariffSection", "TariffChapter", "DutyRate", "FtaRate",
            "DumpingDuty", "Tco", "GstProvision", "TradeAgreement"
        ]
        
        for model_name in models_to_test:
            section_total += 1
            if self.run_test(f"Model {model_name} available in __all__", test_model_availability, model_name):
                section_passed += 1
        
        # Test model class accessibility
        def test_model_class_access():
            try:
                from models import ExportCode, ProductClassification, TariffCode
                
                # Check that classes are actually classes
                return (
                    hasattr(ExportCode, '__tablename__') and
                    hasattr(ProductClassification, '__tablename__') and
                    hasattr(TariffCode, '__tablename__')
                )
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("Model classes are accessible and valid", test_model_class_access):
            section_passed += 1
        
        print_summary("Import and Availability", section_passed, section_total)
        return {"passed": section_passed, "total": section_total}
    def validate_model_structure(self) -> Dict[str, int]:
        """Verify model structure, fields, and constraints."""
        print_header("2. MODEL STRUCTURE VALIDATION")
        
        section_passed = 0
        section_total = 0
        
        # Test ExportCode structure
        def test_export_code_structure():
            try:
                from models import ExportCode
                
                # Check table name
                if ExportCode.__tablename__ != "export_codes":
                    return False
                
                # Check required fields exist
                required_fields = ['id', 'ahecc_code', 'description', 'statistical_unit', 
                                 'corresponding_import_code', 'is_active', 'created_at']
                
                for field in required_fields:
                    if not hasattr(ExportCode, field):
                        print(f"Missing field: {field}")
                        return False
                
                return True
            except Exception as e:
                print(f"Error: {e}")
                return False
        
        section_total += 1
        if self.run_test("ExportCode model structure", test_export_code_structure):
            section_passed += 1
        
        # Test ProductClassification structure
        def test_product_classification_structure():
            try:
                from models import ProductClassification
                
                # Check table name
                if ProductClassification.__tablename__ != "product_classifications":
                    return False
                
                # Check required fields exist
                required_fields = ['id', 'product_description', 'hs_code', 'confidence_score',
                                 'classification_source', 'verified_by_broker', 'broker_user_id', 'created_at']
                
                for field in required_fields:
                    if not hasattr(ProductClassification, field):
                        print(f"Missing field: {field}")
                        return False
                
                return True
            except Exception as e:
                print(f"Error: {e}")
                return False
        
        section_total += 1
        if self.run_test("ProductClassification model structure", test_product_classification_structure):
            section_passed += 1
        
        # Test TariffCode updated structure
        def test_tariff_code_updated_structure():
            try:
                from models import TariffCode
                
                # Check that new relationships exist
                required_relationships = ['export_codes', 'product_classifications']
                
                for rel in required_relationships:
                    if not hasattr(TariffCode, rel):
                        print(f"Missing relationship: {rel}")
                        return False
                
                return True
            except Exception as e:
                print(f"Error: {e}")
                return False
        
        section_total += 1
        if self.run_test("TariffCode updated with new relationships", test_tariff_code_updated_structure):
            section_passed += 1
        
        # Test constraints
        def test_confidence_score_constraint():
            try:
                from models import ProductClassification
                
                # Check if constraint exists in table args
                table_args = getattr(ProductClassification, '__table_args__', ())
                
                # Look for confidence score constraint
                constraint_found = False
                for arg in table_args:
                    if hasattr(arg, 'name') and 'confidence' in str(arg.name).lower():
                        constraint_found = True
                        break
                
                return constraint_found
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("ProductClassification confidence_score constraint", test_confidence_score_constraint):
            section_passed += 1
        
        # Test indexes
        def test_model_indexes():
            try:
                from models import ExportCode, ProductClassification
                
                # Check ExportCode indexes
                export_table_args = getattr(ExportCode, '__table_args__', ())
                export_has_indexes = any(hasattr(arg, 'name') and 'ix_' in str(arg.name) for arg in export_table_args)
                
                # Check ProductClassification indexes
                pc_table_args = getattr(ProductClassification, '__table_args__', ())
                pc_has_indexes = any(hasattr(arg, 'name') and 'ix_' in str(arg.name) for arg in pc_table_args)
                
                return export_has_indexes and pc_has_indexes
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("Model indexes configured", test_model_indexes):
            section_passed += 1
        
        print_summary("Model Structure", section_passed, section_total)
        return {"passed": section_passed, "total": section_total}
    def validate_relationships(self) -> Dict[str, int]:
        """Test model relationships."""
        print_header("3. RELATIONSHIP TESTING")
        
        section_passed = 0
        section_total = 0
        
        # Test TariffCode → ExportCode relationship
        def test_tariff_to_export_relationship():
            try:
                from models import TariffCode
                
                # Check relationship exists
                if not hasattr(TariffCode, 'export_codes'):
                    return False
                
                # Check relationship configuration
                rel = getattr(TariffCode, 'export_codes')
                if not hasattr(rel.property, 'back_populates'):
                    return False
                
                return rel.property.back_populates == 'corresponding_import_tariff'
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("TariffCode → ExportCode relationship", test_tariff_to_export_relationship):
            section_passed += 1
        
        # Test TariffCode → ProductClassification relationship
        def test_tariff_to_classification_relationship():
            try:
                from models import TariffCode
                
                # Check relationship exists
                if not hasattr(TariffCode, 'product_classifications'):
                    return False
                
                # Check relationship configuration
                rel = getattr(TariffCode, 'product_classifications')
                if not hasattr(rel.property, 'back_populates'):
                    return False
                
                return rel.property.back_populates == 'tariff_code'
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("TariffCode → ProductClassification relationship", test_tariff_to_classification_relationship):
            section_passed += 1
        
        # Test ExportCode → TariffCode relationship
        def test_export_to_tariff_relationship():
            try:
                from models import ExportCode
                
                # Check relationship exists
                if not hasattr(ExportCode, 'corresponding_import_tariff'):
                    return False
                
                # Check relationship configuration
                rel = getattr(ExportCode, 'corresponding_import_tariff')
                if not hasattr(rel.property, 'back_populates'):
                    return False
                
                return rel.property.back_populates == 'export_codes'
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("ExportCode → TariffCode relationship", test_export_to_tariff_relationship):
            section_passed += 1
        
        # Test ProductClassification → TariffCode relationship
        def test_classification_to_tariff_relationship():
            try:
                from models import ProductClassification
                
                # Check relationship exists
                if not hasattr(ProductClassification, 'tariff_code'):
                    return False
                
                # Check relationship configuration
                rel = getattr(ProductClassification, 'tariff_code')
                if not hasattr(rel.property, 'back_populates'):
                    return False
                
                return rel.property.back_populates == 'product_classifications'
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("ProductClassification → TariffCode relationship", test_classification_to_tariff_relationship):
            section_passed += 1
        
        # Test foreign key configurations
        def test_foreign_key_configurations():
            try:
                from models import ExportCode, ProductClassification
                
                # Check ExportCode foreign key
                export_fk = getattr(ExportCode, 'corresponding_import_code')
                export_fk_config = export_fk.property.columns[0].foreign_keys
                export_fk_valid = any('tariff_codes.hs_code' in str(fk) for fk in export_fk_config)
                
                # Check ProductClassification foreign key
                pc_fk = getattr(ProductClassification, 'hs_code')
                pc_fk_config = pc_fk.property.columns[0].foreign_keys
                pc_fk_valid = any('tariff_codes.hs_code' in str(fk) for fk in pc_fk_config)
                
                return export_fk_valid and pc_fk_valid
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("Foreign key configurations", test_foreign_key_configurations):
            section_passed += 1
        
        # Test cascade behaviors
        def test_cascade_behaviors():
            try:
                from models import TariffCode
                
                # Check export_codes relationship (should be SET NULL)
                export_rel = getattr(TariffCode, 'export_codes')
                # For SET NULL, the relationship itself doesn't have cascade, it's on the FK
                
                # Check product_classifications relationship (should be CASCADE)
                pc_rel = getattr(TariffCode, 'product_classifications')
                pc_cascade = getattr(pc_rel.property, 'cascade', '')
                
                return 'delete-orphan' in pc_cascade
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("Cascade behaviors configured", test_cascade_behaviors):
            section_passed += 1
        
        print_summary("Relationships", section_passed, section_total)
        return {"passed": section_passed, "total": section_total}
    def validate_helper_methods(self) -> Dict[str, int]:
        """Test helper methods on models."""
        print_header("4. HELPER METHOD TESTING")
        
        section_passed = 0
        section_total = 0
        
        # Test ExportCode helper methods
        def test_export_code_has_import_equivalent():
            try:
                from models import ExportCode
                
                # Create mock instance
                export_code = ExportCode()
                
                # Test with None
                export_code.corresponding_import_code = None
                if export_code.has_import_equivalent():
                    return False
                
                # Test with value
                export_code.corresponding_import_code = "1234567890"
                if not export_code.has_import_equivalent():
                    return False
                
                return True
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("ExportCode.has_import_equivalent()", test_export_code_has_import_equivalent):
            section_passed += 1
        
        def test_export_code_get_statistical_info():
            try:
                from models import ExportCode
                
                export_code = ExportCode()
                
                # Test with None
                export_code.statistical_unit = None
                result = export_code.get_statistical_info()
                if result != "No unit specified":
                    return False
                
                # Test with value
                export_code.statistical_unit = "kg"
                result = export_code.get_statistical_info()
                if result != "kg":
                    return False
                
                return True
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("ExportCode.get_statistical_info()", test_export_code_get_statistical_info):
            section_passed += 1
        
        def test_export_code_is_currently_active():
            try:
                from models import ExportCode
                
                export_code = ExportCode()
                
                # Test True
                export_code.is_active = True
                if not export_code.is_currently_active():
                    return False
                
                # Test False
                export_code.is_active = False
                if export_code.is_currently_active():
                    return False
                
                return True
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("ExportCode.is_currently_active()", test_export_code_is_currently_active):
            section_passed += 1
        
        # Test ProductClassification helper methods
        def test_classification_confidence_level_description():
            try:
                from models import ProductClassification
                
                pc = ProductClassification()
                
                # Test None
                pc.confidence_score = None
                if pc.confidence_level_description() != "Unknown":
                    return False
                
                # Test High (>0.8)
                pc.confidence_score = Decimal('0.9')
                if pc.confidence_level_description() != "High":
                    return False
                
                # Test Medium (0.5-0.8)
                pc.confidence_score = Decimal('0.7')
                if pc.confidence_level_description() != "Medium":
                    return False
                
                # Test Low (<0.5)
                pc.confidence_score = Decimal('0.3')
                if pc.confidence_level_description() != "Low":
                    return False
                
                return True
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("ProductClassification.confidence_level_description()", test_classification_confidence_level_description):
            section_passed += 1
        
        def test_classification_is_verified():
            try:
                from models import ProductClassification
                
                pc = ProductClassification()
                
                # Test True
                pc.verified_by_broker = True
                if not pc.is_verified():
                    return False
                
                # Test False
                pc.verified_by_broker = False
                if pc.is_verified():
                    return False
                
                return True
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("ProductClassification.is_verified()", test_classification_is_verified):
            section_passed += 1
        
        def test_classification_needs_verification():
            try:
                from models import ProductClassification
                
                pc = ProductClassification()
                
                # Test verified (should not need verification)
                pc.verified_by_broker = True
                pc.confidence_score = Decimal('0.5')
                if pc.needs_verification():
                    return False
                
                # Test not verified, None confidence (should need verification)
                pc.verified_by_broker = False
                pc.confidence_score = None
                if not pc.needs_verification():
                    return False
                
                # Test not verified, low confidence (should need verification)
                pc.verified_by_broker = False
                pc.confidence_score = Decimal('0.7')
                if not pc.needs_verification():
                    return False
                
                # Test not verified, high confidence (should not need verification)
                pc.verified_by_broker = False
                pc.confidence_score = Decimal('0.9')
                if pc.needs_verification():
                    return False
                
                return True
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("ProductClassification.needs_verification()", test_classification_needs_verification):
            section_passed += 1
        
        def test_classification_confidence_percentage():
            try:
                from models import ProductClassification
                
                pc = ProductClassification()
                
                # Test None
                pc.confidence_score = None
                if pc.confidence_percentage() != "N/A":
                    return False
                
                # Test value
                pc.confidence_score = Decimal('0.85')
                if pc.confidence_percentage() != "85%":
                    return False
                
                return True
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("ProductClassification.confidence_percentage()", test_classification_confidence_percentage):
            section_passed += 1
        
        print_summary("Helper Methods", section_passed, section_total)
        return {"passed": section_passed, "total": section_total}
    def validate_database_schema_compliance(self) -> Dict[str, int]:
        """Validate database schema compliance."""
        print_header("5. DATABASE SCHEMA COMPLIANCE")
        
        section_passed = 0
        section_total = 0
        
        # Test table names
        def test_table_names():
            try:
                from models import ExportCode, ProductClassification, TariffCode
                
                expected_tables = {
                    ExportCode: "export_codes",
                    ProductClassification: "product_classifications",
                    TariffCode: "tariff_codes"
                }
                
                for model, expected_name in expected_tables.items():
                    if model.__tablename__ != expected_name:
                        print(f"Wrong table name for {model.__name__}: expected {expected_name}, got {model.__tablename__}")
                        return False
                
                return True
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("Table names match schema", test_table_names):
            section_passed += 1
        
        # Test field types
        def test_field_types():
            try:
                from models import ExportCode, ProductClassification
                from sqlalchemy import String, Integer, Text, Boolean, DateTime, DECIMAL
                
                # Check ExportCode field types
                export_checks = [
                    (ExportCode.id.property.columns[0].type, Integer),
                    (ExportCode.ahecc_code.property.columns[0].type, String),
                    (ExportCode.description.property.columns[0].type, Text),
                    (ExportCode.is_active.property.columns[0].type, Boolean),
                    (ExportCode.created_at.property.columns[0].type, DateTime)
                ]
                
                for field_type, expected_type in export_checks:
                    if not isinstance(field_type, expected_type):
                        print(f"Wrong field type: expected {expected_type}, got {type(field_type)}")
                        return False
                
                # Check ProductClassification field types
                pc_checks = [
                    (ProductClassification.id.property.columns[0].type, Integer),
                    (ProductClassification.product_description.property.columns[0].type, Text),
                    (ProductClassification.hs_code.property.columns[0].type, String),
                    (ProductClassification.confidence_score.property.columns[0].type, DECIMAL),
                    (ProductClassification.verified_by_broker.property.columns[0].type, Boolean)
                ]
                
                for field_type, expected_type in pc_checks:
                    if not isinstance(field_type, expected_type):
                        print(f"Wrong field type: expected {expected_type}, got {type(field_type)}")
                        return False
                
                return True
            except Exception as e:
                print(f"Error checking field types: {e}")
                return False
        
        section_total += 1
        if self.run_test("Field types match schema", test_field_types):
            section_passed += 1
        
        # Test foreign key relationships
        def test_foreign_key_schema():
            try:
                from models import ExportCode, ProductClassification
                
                # Check ExportCode foreign key
                export_fk = ExportCode.corresponding_import_code.property.columns[0]
                export_fk_targets = [str(fk.target_fullname) for fk in export_fk.foreign_keys]
                if 'tariff_codes.hs_code' not in export_fk_targets:
                    return False
                
                # Check ProductClassification foreign key
                pc_fk = ProductClassification.hs_code.property.columns[0]
                pc_fk_targets = [str(fk.target_fullname) for fk in pc_fk.foreign_keys]
                if 'tariff_codes.hs_code' not in pc_fk_targets:
                    return False
                
                return True
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("Foreign key relationships match schema", test_foreign_key_schema):
            section_passed += 1
        
        # Test cascade behaviors match schema
        def test_cascade_schema_compliance():
            try:
                from models import ExportCode, ProductClassification
                
                # Check ExportCode FK ondelete (should be SET NULL)
                export_fk = ExportCode.corresponding_import_code.property.columns[0]
                export_fk_ondelete = None
                for fk in export_fk.foreign_keys:
                    if hasattr(fk, 'ondelete'):
                        export_fk_ondelete = fk.ondelete
                        break
                
                # Check ProductClassification FK ondelete (should be CASCADE)
                pc_fk = ProductClassification.hs_code.property.columns[0]
                pc_fk_ondelete = None
                for fk in pc_fk.foreign_keys:
                    if hasattr(fk, 'ondelete'):
                        pc_fk_ondelete = fk.ondelete
                        break
                
                return (export_fk_ondelete == 'SET NULL' and pc_fk_ondelete == 'CASCADE')
            except Exception:
                return False
        
        section_total += 1
        if self.run_test("Cascade behaviors match schema", test_cascade_schema_compliance):
            section_passed += 1
        
        print_summary("Schema Compliance", section_passed, section_total)
        return {"passed": section_passed, "total": section_total}
    
    def validate_integration(self) -> Dict[str, int]:
        """Test integration and model instantiation."""
        print_header("6. INTEGRATION TESTING")
        
        section_passed = 0
        section_total = 0
        
        # Test model instantiation
        def test_model_instantiation():
            try:
                from models import ExportCode, ProductClassification, TariffCode
                
                # Test ExportCode instantiation
                export_code = ExportCode(
                    ahecc_code="1234567890",
                    description="Test export code",
                    statistical_unit="kg",
                    is_active=True
                )
                
                # Test ProductClassification instantiation
                classification = ProductClassification(
                    product_description="Test product",
                    hs_code="1234567890",
                    confidence_score=Decimal('0.85'),
                    classification_source="ai",
                    verified_by_broker=False
                )
                
                # Test TariffCode instantiation
                tariff_code = TariffCode(
                    hs_code="1234567890",
                    description="Test tariff code",
                    level=10,
                    is_active=True
                )
                
                return True
            except Exception as e:
                print(f"Instantiation error: {e}")
                return False
        
        section_total += 1
        if self.run_test("Model instantiation", test_model_instantiation):
            section_passed += 1
        
        # Test relationship assignment
        def test_relationship_assignment():
            try:
                from models import ExportCode, ProductClassification, TariffCode
                
                # Create instances
                tariff_code = TariffCode(
                    hs_code="1234567890",
                    description="Test tariff code",
                    level=10,
                    is_active=True
                )
                
                export_code = ExportCode(
                    ahecc_code="1234567890",
                    description="Test export code",
                    corresponding_import_code="1234567890",
                    is_active=True
                )
                
                classification = ProductClassification(
                    product_description="Test product",
                    hs_code="1234567890",
                    confidence_score=Decimal('0.85'),
                    verified_by_broker=False
                )
                
                # Test relationship assignment
                export_code.corresponding_import_tariff = tariff_code
                classification.tariff_code = tariff_code
                
                return True
            except Exception as e:
                print(f"Relationship assignment error: {e}")
                return False
        
        section_total += 1
        if self.run_test("Relationship assignment", test_relationship_assignment):
            section_passed += 1
        
        # Test string representations
        def test_string_representations():
            try:
                from models import ExportCode, ProductClassification, TariffCode
                
                export_code = ExportCode(
                    id=1,
                    ahecc_code="1234567890",
                    description="Test export code"
                )
                
                classification = ProductClassification(
                    id=1,
                    hs_code="1234567890",
                    product_description="Test product",
                    confidence_score=Decimal('0.85'),
                    verified_by_broker=False
                )
                
                # Test __repr__ and __str__ methods
                export_repr = repr(export_code)
                export_str = str(export_code)
                
                classification_repr = repr(classification)
                classification_str = str(classification)
                
                return (
                    "ExportCode" in export_repr and
                    "1234567890" in export_str and
                    "ProductClassification" in classification_repr and
                    "Test product" in classification_str
                )
            except Exception as e:
                print(f"String representation error: {e}")
                return False
        
        section_total += 1
        if self.run_test("String representations", test_string_representations):
            section_passed += 1
        
        # Test model rebuild functionality
        def test_model_rebuild():
            try:
                from models import ExportCode, ProductClassification, TariffCode
                
                # Test that model_rebuild() can be called without errors
                TariffCode.model_rebuild()
                ExportCode.model_rebuild()
                ProductClassification.model_rebuild()
                
                return True
            except Exception as e:
                print(f"Model rebuild error: {e}")
                return False
        
        section_total += 1
        if self.run_test("Model rebuild functionality", test_model_rebuild):
            section_passed += 1
        
        print_summary("Integration Testing", section_passed, section_total)
        return {"passed": section_passed, "total": section_total}
    
    def run_all_validations(self) -> None:
        """Run all validation tests and provide comprehensive report."""
        print_header("CUSTOMS BROKER PORTAL - COMPREHENSIVE ORM VALIDATION")
        print("Testing complete ORM implementation including new models and relationships")
        print(f"Timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all validation sections
        results = []
        
        try:
            results.append(self.validate_import_and_availability())
            results.append(self.validate_model_structure())
            results.append(self.validate_relationships())
            results.append(self.validate_helper_methods())
            results.append(self.validate_database_schema_compliance())
            results.append(self.validate_integration())
        except Exception as e:
            print(f"\nCRITICAL ERROR during validation: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return
        
        # Calculate overall results
        total_passed = sum(r["passed"] for r in results)
        total_tests = sum(r["total"] for r in results)
        overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Print final summary
        print_header("FINAL VALIDATION SUMMARY")
        print(f"Total Tests Run: {total_tests}")
        print(f"Tests Passed: {total_passed}")
        print(f"Tests Failed: {total_tests - total_passed}")
        print(f"Success Rate: {overall_percentage:.1f}%")
        
        if overall_percentage == 100:
            print("\n🎉 ALL TESTS PASSED! The complete ORM implementation is working correctly.")
            print("✅ All models are properly imported and accessible")
            print("✅ Model structures match requirements")
            print("✅ All relationships are correctly configured")
            print("✅ Helper methods are functioning as expected")
            print("✅ Database schema compliance verified")
            print("✅ Integration testing successful")
        elif overall_percentage >= 90:
            print(f"\n⚠️  MOSTLY SUCCESSFUL with {total_tests - total_passed} minor issues to address.")
        elif overall_percentage >= 70:
            print(f"\n⚠️  PARTIAL SUCCESS with {total_tests - total_passed} issues that need attention.")
        else:
            print(f"\n❌ SIGNIFICANT ISSUES DETECTED. {total_tests - total_passed} tests failed.")
            print("Please review the failed tests above and address the issues.")
        
        print(f"\nValidation completed at {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Main execution function."""
    try:
        validator = ORMValidator()
        validator.run_all_validations()
        
        # Return appropriate exit code
        if validator.failed_tests == 0:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Some tests failed
            
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()