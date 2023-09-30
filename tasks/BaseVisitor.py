from abc import ABC, abstractmethod
import tasks.BaseTasks as BaseTasks
import tasks.AreaTasks as AreaTasks
import tasks.ImageTasks as ImageTasks
import tasks.MultipleImagesTasks as MultipleImagesTasks


class BaseVisitor(ABC):
    def visit(self, task: BaseTasks.BaseTask):
        methods = {
            # AreaTasks
            AreaTasks.SensorMeanRowDeviation: self.visit_AreaSensorMeanRowDeviation,
            AreaTasks.SensorMeanColumnDeviation: self.visit_AreaSensorMeanColumnDeviation,
            AreaTasks.AreaMean: self.visit_AreaAreaMean,

            # ImageTasks
            ImageTasks.BBTask: self.visit_ImageBBTask,
            ImageTasks.SVTask: self.visit_ImageSVTask,

            # MultipleImagesTasks
            MultipleImagesTasks.MultipleImagesCalibrationTask: self.visit_MultipleImagesCalibrationTask,
            MultipleImagesTasks.DeviationsLinearRegression: self.visit_DeviationsLinearRegression,
            MultipleImagesTasks.DeviationsBySurface: self.visit_DeviationsBySurface,
            MultipleImagesTasks.DeviationsByMirrorSide: self.visit_DeviationsByMirrorSide,
            MultipleImagesTasks.DeviationsMeanPerImage: self.visit_DeviationsMeanPerImage,
            MultipleImagesTasks.RegressByYear: self.visit_RegressByYear,
            MultipleImagesTasks.SensorsCoefficientsTask: self.visit_SensorsCoefficientsTask,
        }

        for task_type, visitor_method in methods.items():
            if isinstance(task, task_type):
                visitor_method(task)
                return

    def visit_AreaSensorMeanRowDeviation(self, task: AreaTasks.SensorMeanRowDeviation):
        pass

    def visit_AreaSensorMeanColumnDeviation(self, task: AreaTasks.SensorMeanColumnDeviation):
        pass

    def visit_AreaAreaMean(self, task: AreaTasks.AreaMean):
        pass

    def visit_ImageBBTask(self, task: ImageTasks.BBTask):
        pass

    def visit_ImageSVTask(self, task: ImageTasks.SVTask):
        pass

    def visit_RegressByYear(self, task: MultipleImagesTasks.RegressByYear):
        pass

    def visit_DeviationsLinearRegression(self, task: MultipleImagesTasks.DeviationsLinearRegression):
        pass

    def visit_DeviationsBySurface(self, task: MultipleImagesTasks.DeviationsBySurface):
        pass

    def visit_DeviationsByMirrorSide(self, task: MultipleImagesTasks.DeviationsByMirrorSide):
        pass

    def visit_DeviationsMeanPerImage(self, task: MultipleImagesTasks.DeviationsMeanPerImage):
        pass

    def visit_MultipleImagesCalibrationTask(self, task: MultipleImagesTasks.MultipleImagesCalibrationTask):
        pass

    def visit_SensorsCoefficientsTask(self, task: MultipleImagesTasks.SensorsCoefficientsTask):
        pass