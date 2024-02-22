from abc import ABC
import tasks.BaseTasks as BaseTasks
import tasks.AreaTasks as AreaTasks
import tasks.ImageTasks as ImageTasks
import tasks.MultipleImagesTasks as MultipleImagesTasks
import tasks.DatabaseTasks as DatabaseTasks


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

            # DatabaseTasks
            DatabaseTasks.DeviationsBySurface: self.visit_DeviationsBySurface,
            DatabaseTasks.DeviationsByMirrorSide: self.visit_DeviationsByMirrorSide,
            DatabaseTasks.SensorsCoefficientsTaskByMirror: self.visit_SensorsCoefficientsTaskByMirror,
            DatabaseTasks.SensorsCoefficientsTaskBySurface: self.visit_SensorsCoefficientsTaskBySurface,
            DatabaseTasks.SensorsCoefficientsTask: self.visit_SensorsCoefficientsTask,
            DatabaseTasks.AreaAvgStdTask: self.visit_AreaAvgStdTask,
            DatabaseTasks.RegressByYear: self.visit_RegressByYear,
            DatabaseTasks.NeighboringMirrorsDifference: self.visit_NeighboringMirrorsDifference,
            DatabaseTasks.FindSpectreBrightness: self.visit_FindSpectreBrightness,
            DatabaseTasks.DeviationsByY: self.visit_DeviationsByY,
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

    def visit_RegressByYear(self, task: DatabaseTasks.RegressByYear):
        pass

    def visit_DeviationsBySurface(self, task: DatabaseTasks.DeviationsBySurface):
        pass

    def visit_DeviationsByMirrorSide(self, task: DatabaseTasks.DeviationsByMirrorSide):
        pass

    def visit_MultipleImagesCalibrationTask(self, task: MultipleImagesTasks.MultipleImagesCalibrationTask):
        pass

    def visit_SensorsCoefficientsTaskByMirror(self, task: DatabaseTasks.SensorsCoefficientsTaskByMirror):
        pass

    def visit_SensorsCoefficientsTaskBySurface(self, task: DatabaseTasks.SensorsCoefficientsTaskBySurface):
        pass

    def visit_SensorsCoefficientsTask(self, task: DatabaseTasks.SensorsCoefficientsTask):
        pass

    def visit_AreaAvgStdTask(self, task: DatabaseTasks.AreaAvgStdTask):
        pass

    def visit_NeighboringMirrorsDifference(self, task: DatabaseTasks.NeighboringMirrorsDifference):
        pass

    def visit_FindSpectreBrightness(self, task: DatabaseTasks.FindSpectreBrightness):
        pass

    def visit_DeviationsByY(self, task: DatabaseTasks.DeviationsByY):
        pass