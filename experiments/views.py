from django.shortcuts import render
# Create your views here.
import os
from rest_framework import generics, status, viewsets #, permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from private_storage.views import PrivateStorageDetailView
from .models import Experiment, Screenshot, Variations, ExperimentStatusChoice
from .serializers import ExperimentSerializer, VariationsSerializer
from users.models import CustomUser
from .functions import execute_experiment
from django.http import FileResponse
import json
from agosuirpa.system_configuration import sep
from django.shortcuts import get_object_or_404
import datetime
from django.utils import timezone
from .utils import compress_experiment, upload_mockups
from PIL import Image

def json_attributes_load(att):
    if att:
        att = json.loads(att)
    return att
class VariationsViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticatedUser]
    queryset = Variations.objects.all()
    serializer_class = VariationsSerializer
    
class ExperimentView(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticatedUser]
    serializer_class = ExperimentSerializer

    def get_queryset(self):
        user = self.request.user
        experiments = []
        if(user.is_anonymous is False):
            user = CustomUser.objects.get(id=self.request.user.id)
            experiments = Experiment.objects.filter(user=user.id, is_active=True).order_by("-created_at")
        return experiments

    def post(self, request, *args, **kwargs):
        st = status.HTTP_201_CREATED
        msg = 'ok, created'

        try:
            user = CustomUser.objects.get(id=self.request.user.id)
        except:
            return Response({"message": "No user found"}, status=status.HTTP_404_NOT_FOUND)

        execute_mode=request.data.get('execute_mode')
        try:
            if request.data.get('status') == ExperimentStatusChoice.PR.value:
                for data in ['name', 'screenshots',
                     'special_colnames', 'screenshot_name_generation_function']:
                    if not data in request.data:
                        return Response({"message": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)
                
                experiment = Experiment(
                    size_balance=json_attributes_load(request.data.get('size_balance')),
                    name=request.data.get('name'),
                    description=request.data.get('description'),
                    number_scenarios=int(request.data.get('number_scenarios')) if request.data.get('number_scenarios') else None,
                    variability_conf=json_attributes_load(request.data.get('variability_conf')),
                    scenarios_conf=json_attributes_load(request.data.get('scenarios_conf')) if request.data.get('scenarios_conf') else None,
                    special_colnames=json_attributes_load(request.data.get('special_colnames')),
                    screenshots=request.data.get('screenshots'),
                    user=user,
                    screenshot_name_generation_function=request.data.get('screenshot_name_generation_function'),
                    status=request.data.get('status'),
                )    
            else:
                if execute_mode:
                    if request.data.get('number_scenarios') and int(request.data.get('number_scenarios')) > 0 and not ('scenarios_conf' in request.data):
                        return Response({"message": "Number scenarios greater than 1 and no scenario configuration included!"}, status=status.HTTP_400_BAD_REQUEST)
                    for data in ['size_balance', 'name', 'number_scenarios', 
                        'variability_conf', 'screenshots',
                        'special_colnames', 'screenshot_name_generation_function']:
                        if not data in request.data:
                            return Response({"message": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    for data in ['name', 'special_colnames', 'screenshot_name_generation_function']:
                        if not data in request.data:
                            return Response({"message": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)
       
                
                experiment = Experiment(
                    size_balance=json_attributes_load(request.data.get('size_balance')),
                    name=request.data.get('name'),
                    description=request.data.get('description'),
                    number_scenarios=int(request.data.get('number_scenarios')) if request.data.get('number_scenarios') else None,
                    variability_conf=json_attributes_load(request.data.get('variability_conf')),
                    scenarios_conf=json_attributes_load(request.data.get('scenarios_conf')) if request.data.get('scenarios_conf') else None,
                    special_colnames=json_attributes_load(request.data.get('special_colnames')),
                    screenshots=request.data.get('screenshots'),
                    user=user,
                    screenshot_name_generation_function=request.data.get('screenshot_name_generation_function'),
                )

            experiment.save()
            
            if 'screenshots' in request.data:
                # if experiment.status == ExperimentStatusChoice.PR or experiment.status == ExperimentStatusChoice.LA:
                path_without_fileextension = upload_mockups('privatefiles'+sep+experiment.screenshots.name)
                experiment.screenshots_path=path_without_fileextension
                associate_screenshots_files(experiment)
                experiment.last_edition = datetime.datetime.now(tz=timezone.utc)
            
            if execute_mode:
                experiment.execution_start = datetime.datetime.now(tz=timezone.utc)
                experiment.foldername=execute_experiment(experiment)
                experiment.execution_finish = datetime.datetime.now(tz=timezone.utc)
                experiment.is_being_processed=100
                experiment.is_active=True
                experiment.status=ExperimentStatusChoice.LA.value
            elif request.data.get('status') != ExperimentStatusChoice.PR.value:
                experiment.status=ExperimentStatusChoice.SA.value
            experiment.save()
            
            response_content = {"message": msg, "id": experiment.id, "status": experiment.status}
            
        except Exception as e:
            msg = 'Some of atributes are invalid: ' + str(e)
            st = status.HTTP_422_UNPROCESSABLE_ENTITY
            response_content = {"message": msg}

        return Response(response_content, status=st)

   
class ExperimentUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExperimentSerializer
    queryset = Experiment.objects.all()
    lookup_field = 'id'
    
    def get(self, request, id, *args, **kwargs):
        experiment = get_object_or_404(Experiment, user=request.user.id, id=id)
        return Response(ExperimentSerializer(experiment).data)
    
    def put(self, request, id, *args, **kwars):
        user = request.user
        st = status.HTTP_200_OK
        msg = "Experiment updated"
        
        if(user.is_anonymous is False):
            user = get_object_or_404(CustomUser, id=request.user.id)
            experiment = get_object_or_404(Experiment, user=user.id, id=id)
            
            try:
                execute_mode=request.data.get('execute_mode')
                wizard_mode=request.data.get('wizard_mode')
                if wizard_mode == "scenario":
                        experiment.scenarios_conf=json_attributes_load(request.data.get('scenarios_conf'))
                elif wizard_mode == "variability":
                        experiment.variability_conf=json_attributes_load(request.data.get('variability_conf'))
                else:
                    if execute_mode:
                        for data in ['size_balance', 'name', 'description', 'number_scenarios', 
                            'variability_conf', 'screenshots',
                            'special_colnames', 'screenshot_name_generation_function']:
                            if not data in request.data or (int(request.data.get('number_scenarios')) > 0 and not ('scenarios_conf' in request.data)):
                                return Response({"message": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        for data in ['name', 'special_colnames', 'screenshot_name_generation_function']:
                            if not data in request.data:
                                return Response({"message": "Incomplete data"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    experiment.size_balance=json_attributes_load(request.data.get('size_balance')),
                    experiment.name=request.data.get('name'),
                    experiment.description=request.data.get('description'),
                    experiment.number_scenarios=int(request.data.get('number_scenarios')) if request.data.get('number_scenarios') else None,
                    experiment.variability_conf=json_attributes_load(request.data.get('variability_conf')),
                    experiment.scenarios_conf=json_attributes_load(request.data.get('scenarios_conf')),
                    experiment.special_colnames=json_attributes_load(request.data.get('special_colnames')),
                    experiment.screenshots=request.data.get('screenshots'),
                    experiment.user=user,
                    experiment.screenshot_name_generation_function=request.data.get('screenshot_name_generation_function'),

                    experiment.save()
                    
                    if 'screenshots' in request.data and experiment.screenshots != request.data.get('screenshots'):
                        # if experiment.status == ExperimentStatusChoice.PR or experiment.status == ExperimentStatusChoice.LA:
                        path_without_fileextension = upload_mockups('privatefiles'+sep+experiment.screenshots.name)
                        experiment.screenshots_path=path_without_fileextension
                        associate_screenshots_files(experiment)
                        experiment.last_edition = datetime.datetime.now(tz=timezone.utc)
                    
                    if execute_mode:
                        experiment.execution_start = datetime.datetime.now(tz=timezone.utc)
                        experiment.foldername=execute_experiment(experiment)
                        experiment.execution_finish = datetime.datetime.now(tz=timezone.utc)
                        experiment.is_being_processed=100
                        experiment.is_active=True
                        experiment.status=ExperimentStatusChoice.LA.value
                    elif request.data.get('status') != ExperimentStatusChoice.PR.value:
                        experiment.status=ExperimentStatusChoice.SA.value
                experiment.save()
            except Exception as e:
                msg = 'Some of atributes are invalid: ' + str(e)
                st = status.HTTP_422_UNPROCESSABLE_ENTITY 
        else:
            msg = "No user valid"
            st=status.HTTP_401_UNAUTHORIZED
        
        return Response({"message": msg}, status=st)
        
    def delete(self, request, id, *args, **kwars):
        st = status.HTTP_200_OK
        msg = 'deleted'

        try:
            experiment = get_object_or_404(Experiment, pk=id, user=request.user.id)
            experiment.delete()
        except Exception as e:
            msg = 'Cannot delete experiment: ' + str(e)
            st = status.HTTP_409_CONFLICT

        return Response(msg, status=st)
    
class SmallPagesPagination(PageNumberPagination):
    page_size = 8


class ListPaginatedExperimentAPIView(generics.ListAPIView):
    """
    List active experiments
    """
    pagination_class = SmallPagesPagination
    # permission_classes = [IsAuthenticatedAdmin]
    serializer_class = ExperimentSerializer

    def get_queryset(self):
        user = self.request.user
        if(user.is_anonymous is False):
            user_id = CustomUser.objects.get(user_account=self.request.user).id
            queryset = Experiment.objects.filter(user=user_id, is_active=True)
        return queryset

class DownloadExperiment(generics.RetrieveAPIView):
    """
    Download compress experiment
    """
    def get(self, request, *args, **kwargs):
        msg = "Experiment downloaded"
        st=status.HTTP_200_OK
        user = get_object_or_404(CustomUser, id=request.user.id)
        if(user.is_anonymous is False):
            experiment = get_object_or_404(Experiment, user=user.id, is_being_processed=100, id=kwargs["pk"])
            try:        
                zip_experiment = compress_experiment(experiment.foldername, experiment.name.replace(" ", "_") + "_" + str(experiment.id))
                filename = experiment.name.replace(" ", "_") + "_" + str(experiment.id) + ".zip"
                response = FileResponse(open(zip_experiment, 'rb'))
                response['Content-Disposition'] = 'attachment; filename="%s"' % filename  
            except Exception as e:
                msg = "Experiment error: " + str(e)
                st=status.HTTP_405_METHOD_NOT_ALLOWED
                response = Response({"message": msg}, status=st)
        else:
            msg = "No user valid" + str(e)
            st=status.HTTP_401_UNAUTHORIZED
            response = Response({"message": msg}, status=st)
        
        return response

def associate_experiment(user):
    basic_path_template_experiments='resources'+sep+'template_experiments'+sep
    experiments = Experiment.objects.filter(user=user.id, is_active=True)
    if experiments == None or not experiments:
        data_complete = json.load(open(basic_path_template_experiments+'experiments_template.json'))
        for data in data_complete['results']:
            size_balance=data['size_balance']
            name=data['name']
            description=data['description']
            number_scenarios=int(data['number_scenarios'])
            variability_conf=data['variability_conf']
            screenshots=data['screenshots']
            special_colnames=data['special_colnames']
            screenshot_name_generation_function=data['screenshot_name_generation_function']
            foldername=data['foldername']
            scenarios_conf=data['scenarios_conf']

            experiment = Experiment(
                scenarios_conf=scenarios_conf,
                size_balance=size_balance,
                name=name,
                description=description,
                number_scenarios=number_scenarios,
                variability_conf=variability_conf,
                special_colnames=special_colnames,
                screenshots=screenshots,
                foldername=foldername,
                is_being_processed=100,
                is_active=True,
                user=user,
                screenshot_name_generation_function=screenshot_name_generation_function,
                screenshots_path=basic_path_template_experiments+(screenshots)
            )
            experiment.user=user
            experiment.save()

# https://github.com/edoburu/django-private-storage
# class ScreenshotDownloadView(PrivateStorageDetailView):
#     model = Screenshot
#     model_file_field = 'image'

#     def get_queryset(self):
#         # Make sure only certain objects can be accessed.
#         return super().get_queryset().filter(...)

#     def can_access_file(self, private_file):
#         # When the object can be accessed, the file may be downloaded.
#         # This overrides PRIVATE_STORAGE_AUTH_FUNCTION
#         return True

def associate_screenshots_files(experiment):
    for root, directories, file in os.walk(experiment.screenshots_path):
        for file in file:
            if(file.endswith(".png") or file.endswith(".jpg")):
                image = Image.open(os.path.join(root, file))
                aux = experiment.screenshots_path.split(sep)
                width, height = image.size
                relative_path = aux[len(aux)-1]+sep+file
                screenshot = Screenshot(relative_path=relative_path, width=width, height=height, image=file, experiment=experiment)
                screenshot.save()