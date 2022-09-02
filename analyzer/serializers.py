from rest_framework import serializers
from .models import CaseStudy, ClassifyImageComponents, DecisionTreeTraining, ExtractTrainingDataset, GUIComponentDetection

class CaseStudySerializer(serializers.ModelSerializer):
    phases_to_execute = serializers.JSONField()
    special_colnames = serializers.JSONField()
    class Meta:
        model = CaseStudy
        fields = '__all__' # ['id', 'title', 'created_at', 'mode', 'exp_version_name', 'phases_to_execute', 'decision_point_activity', 'path_to_save_experiment', 'gui_class_success_regex', 'gui_quantity_difference', 'scenarios_to_study', 'drop', 'user']

class GUIComponentDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GUIComponentDetection
        fields = '__all__' # ['eyetracking_log_filename', 'add_words_columns', 'overwrite_npy']

class ClassifyImageComponentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifyImageComponents
        fields = ['model_json_file_name', 'model_weights']

class ExtractTrainingDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractTrainingDataset
        fields = '__all__' # ['columns_to_ignore']
    
class DecisionTreeTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionTreeTraining
        fields = '__all__' # ['library', 'algorithms', 'mode', 'columns_to_ignore']