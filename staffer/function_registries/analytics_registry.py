"""Analytics function registry for Staffer."""

from google.genai import types

# Import analytics tools functions and schemas
from ..functions.analytics.tools.analyze_distributions_tool import schema_analyze_distributions, analyze_distributions
from ..functions.analytics.tools.calculate_feature_importance_tool import schema_calculate_feature_importance, calculate_feature_importance
from ..functions.analytics.tools.compare_datasets_tool import schema_compare_datasets, compare_datasets
from ..functions.analytics.tools.create_chart_tool import schema_create_chart as schema_create_analytic_chart_html, create_chart as create_analytic_chart_html
from ..functions.analytics.tools.detect_outliers_tool import schema_detect_outliers, detect_outliers
from ..functions.analytics.tools.execute_custom_analytics_code_tool import schema_execute_custom_analytics_code, execute_custom_analytics_code
from ..functions.analytics.tools.export_insights_tool import schema_export_insights, export_insights
from ..functions.analytics.tools.find_correlations_tool import schema_find_correlations, find_correlations
from ..functions.analytics.tools.generate_dashboard_tool import schema_generate_dashboard, generate_dashboard
from ..functions.analytics.tools.list_loaded_datasets_tool import schema_list_loaded_datasets, list_loaded_datasets
from ..functions.analytics.tools.load_dataset_tool import schema_load_dataset, load_dataset
from ..functions.analytics.tools.memory_optimization_report_tool import schema_memory_optimization_report, memory_optimization_report
from ..functions.analytics.tools.merge_datasets_tool import schema_merge_datasets, merge_datasets
from ..functions.analytics.tools.segment_by_column_tool import schema_segment_by_column, segment_by_column
from ..functions.analytics.tools.suggest_analysis_tool import schema_suggest_analysis, suggest_analysis
from ..functions.analytics.tools.time_series_analysis_tool import schema_time_series_analysis, time_series_analysis
from ..functions.analytics.tools.validate_data_quality_tool import schema_validate_data_quality, validate_data_quality

# Import analytics resources functions and schemas
from ..functions.analytics.resources.get_analysis_suggestions_resource import schema_get_analysis_suggestions, get_analysis_suggestions
from ..functions.analytics.resources.get_available_analyses_resource import schema_get_available_analyses, get_available_analyses
from ..functions.analytics.resources.get_column_types_resource import schema_get_column_types, get_column_types
from ..functions.analytics.resources.get_current_dataset_resource import schema_get_current_dataset, get_current_dataset
from ..functions.analytics.resources.get_dataset_sample_resource import schema_get_dataset_sample, get_dataset_sample
from ..functions.analytics.resources.get_dataset_schema_resource import schema_get_dataset_schema, get_dataset_schema
from ..functions.analytics.resources.get_dataset_summary_resource import schema_get_dataset_summary, get_dataset_summary
from ..functions.analytics.resources.get_loaded_datasets_resource import schema_get_loaded_datasets, get_loaded_datasets
from ..functions.analytics.resources.get_memory_usage_resource import schema_get_memory_usage, get_memory_usage
from ..functions.analytics.resources.get_server_config_resource import schema_get_server_config, get_server_config
from ..functions.analytics.resources.get_system_status_resource import schema_get_system_status, get_system_status
from ..functions.analytics.resources.get_user_profile_resource import schema_get_user_profile, get_user_profile

# Import all functions from data_resources
from ..functions.analytics.resources.data_resources import (
    get_server_config as dr_get_server_config,
    get_loaded_datasets as dr_get_loaded_datasets,
    get_dataset_schema as dr_get_dataset_schema,
    get_dataset_summary as dr_get_dataset_summary,
    get_dataset_sample as dr_get_dataset_sample,
    get_current_dataset as dr_get_current_dataset,
    get_available_analyses as dr_get_available_analyses,
    get_column_types as dr_get_column_types,
    get_analysis_suggestions as dr_get_analysis_suggestions,
    get_memory_usage as dr_get_memory_usage,
    get_user_profile as dr_get_user_profile,
    get_system_status as dr_get_system_status,
    # Schemas from data_resources
    schema_get_server_config as dr_schema_get_server_config,
    schema_get_loaded_datasets as dr_schema_get_loaded_datasets,
    schema_get_dataset_schema as dr_schema_get_dataset_schema,
    schema_get_dataset_summary as dr_schema_get_dataset_summary,
    schema_get_dataset_sample as dr_schema_get_dataset_sample,
    schema_get_current_dataset as dr_schema_get_current_dataset,
    schema_get_available_analyses as dr_schema_get_available_analyses,
    schema_get_column_types as dr_schema_get_column_types,
    schema_get_analysis_suggestions as dr_schema_get_analysis_suggestions,
    schema_get_memory_usage as dr_schema_get_memory_usage,
    schema_get_user_profile as dr_schema_get_user_profile,
    schema_get_system_status as dr_schema_get_system_status,
)

# Import analytics prompts functions and schemas
from ..functions.analytics.prompts.correlation_investigation_prompt import schema_correlation_investigation, correlation_investigation
from ..functions.analytics.prompts.dashboard_design_consultation_prompt import schema_dashboard_design_consultation, dashboard_design_consultation
from ..functions.analytics.prompts.data_quality_assessment_prompt import schema_data_quality_assessment, data_quality_assessment
from ..functions.analytics.prompts.dataset_first_look_prompt import schema_dataset_first_look, dataset_first_look
from ..functions.analytics.prompts.find_datasources_prompt import schema_find_datasources, find_datasources
from ..functions.analytics.prompts.insight_generation_workshop_prompt import schema_insight_generation_workshop, insight_generation_workshop
from ..functions.analytics.prompts.list_analytics_assets_prompt import schema_list_analytics_assets, list_analytics_assets
from ..functions.analytics.prompts.pattern_discovery_session_prompt import schema_pattern_discovery_session, pattern_discovery_session
from ..functions.analytics.prompts.segmentation_workshop_prompt import schema_segmentation_workshop, segmentation_workshop

# Analytics schemas list
analytics_schemas = [
    # Tools (17)
    schema_analyze_distributions,
    schema_calculate_feature_importance,
    schema_compare_datasets,
    schema_create_analytic_chart_html,
    schema_detect_outliers,
    schema_execute_custom_analytics_code,
    schema_export_insights,
    schema_find_correlations,
    schema_generate_dashboard,
    schema_list_loaded_datasets,
    schema_load_dataset,
    schema_memory_optimization_report,
    schema_merge_datasets,
    schema_segment_by_column,
    schema_suggest_analysis,
    schema_time_series_analysis,
    schema_validate_data_quality,
    # Resources (13) - Use individual resource schemas, not from data_resources
    schema_get_analysis_suggestions,
    schema_get_available_analyses,
    schema_get_column_types,
    schema_get_current_dataset,
    schema_get_dataset_sample,
    schema_get_dataset_schema,
    schema_get_dataset_summary,
    schema_get_loaded_datasets,
    schema_get_memory_usage,
    schema_get_server_config,
    schema_get_system_status,
    schema_get_user_profile,
    # Prompts (9)
    schema_correlation_investigation,
    schema_dashboard_design_consultation,
    schema_data_quality_assessment,
    schema_dataset_first_look,
    schema_find_datasources,
    schema_insight_generation_workshop,
    schema_list_analytics_assets,
    schema_pattern_discovery_session,
    schema_segmentation_workshop,
]

# Analytics function mapping
analytics_functions = {
    # Tools (17)
    "analyze_distributions": analyze_distributions,
    "calculate_feature_importance": calculate_feature_importance,
    "compare_datasets": compare_datasets,
    "create_analytic_chart_html": create_analytic_chart_html,
    "detect_outliers": detect_outliers,
    "execute_custom_analytics_code": execute_custom_analytics_code,
    "export_insights": export_insights,
    "find_correlations": find_correlations,
    "generate_dashboard": generate_dashboard,
    "list_loaded_datasets": list_loaded_datasets,
    "load_dataset": load_dataset,
    "memory_optimization_report": memory_optimization_report,
    "merge_datasets": merge_datasets,
    "segment_by_column": segment_by_column,
    "suggest_analysis": suggest_analysis,
    "time_series_analysis": time_series_analysis,
    "validate_data_quality": validate_data_quality,
    # Resources (13) - Use individual resource functions, not from data_resources
    "get_analysis_suggestions": get_analysis_suggestions,
    "get_available_analyses": get_available_analyses,
    "get_column_types": get_column_types,
    "get_current_dataset": get_current_dataset,
    "get_dataset_sample": get_dataset_sample,
    "get_dataset_schema": get_dataset_schema,
    "get_dataset_summary": get_dataset_summary,
    "get_loaded_datasets": get_loaded_datasets,
    "get_memory_usage": get_memory_usage,
    "get_server_config": get_server_config,
    "get_system_status": get_system_status,
    "get_user_profile": get_user_profile,
    # Prompts (9)
    "correlation_investigation": correlation_investigation,
    "dashboard_design_consultation": dashboard_design_consultation,
    "data_quality_assessment": data_quality_assessment,
    "dataset_first_look": dataset_first_look,
    "find_datasources": find_datasources,
    "insight_generation_workshop": insight_generation_workshop,
    "list_analytics_assets": list_analytics_assets,
    "pattern_discovery_session": pattern_discovery_session,
    "segmentation_workshop": segmentation_workshop,
}