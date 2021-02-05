import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import NodeModify, toBool, VTKObservationMixin

from Resources import QReadsResources
#
# QReads
#

class QReads(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "QReads"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["SlicerQReads"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#QReads">module documentation</a>.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

    # Additional initialization step after application startup is complete
    #slicer.app.connect("startupCompleted()", registerSampleData)


#
# QReadsWidget
#

class QReadsWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False
    self.slabModeButtonGroup = None

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/QReads.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)
    self.slabModeButtonGroup = qt.QButtonGroup()
    self.slabModeButtonGroup.addButton(self.ui.SlabModeMaxRadioButton, vtk.VTK_IMAGE_SLAB_MAX)
    self.slabModeButtonGroup.addButton(self.ui.SlabModeMeanRadioButton, vtk.VTK_IMAGE_SLAB_MEAN)
    self.slabModeButtonGroup.addButton(self.ui.SlabModeMinRadioButton, vtk.VTK_IMAGE_SLAB_MIN)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = QReadsLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.NodeAddedEvent, self.onNodeAdded)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.SlabButton.connect("clicked()", self.updateParameterNodeFromGUI)
    self.slabModeButtonGroup.connect("buttonClicked(int)", self.updateParameterNodeFromGUI)
    self.ui.SlabThicknessSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    self.ui.InverseGrayButton.connect("clicked(bool)", self.updateParameterNodeFromGUI)
    self.ui.CTBodySoftTissueWLPresetButton.connect("clicked()", lambda presetName="CT-BodySoftTissue": self.logic.setWindowLevelPreset(presetName))
    self.ui.CTBoneWLPresetButton.connect("clicked()", lambda presetName="CT-Bone": self.logic.setWindowLevelPreset(presetName))
    self.ui.CTBrainWLPresetButton.connect("clicked()", lambda presetName="CT-Head": self.logic.setWindowLevelPreset(presetName))
    self.ui.CTLungWLPresetButton.connect("clicked()", lambda presetName="CT-Lung": self.logic.setWindowLevelPreset(presetName))

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

    # Hide main window components
    slicer.util.setApplicationLogoVisible(False)
    slicer.util.setMenuBarsVisible(False)
    slicer.util.setModuleHelpSectionVisible(False)
    slicer.util.setModulePanelTitleVisible(False)
    slicer.util.setToolbarsVisible(False)

    # Layout
    slicer.app.layoutManager().setLayout(self.logic.registerCustomLayout())

    for viewName, viewColor in QReadsLogic.SLICEVIEW_BACKGROUND_COLORS.items():
      sliceWidget = slicer.app.layoutManager().sliceWidget(viewName)
      sliceWidget.sliceView().setBackgroundColor(qt.QColor(viewColor))
      sliceWidget.mrmlSliceNode().SetOrientationMarkerType(slicer.vtkMRMLAbstractViewNode.OrientationMarkerTypeAxes)

    for viewName, viewColor in QReadsLogic.THREEDVIEW_BACKGROUND_COLORS.items():
      with NodeModify(slicer.util.getNode("vtkMRMLViewNode%s" % viewName)) as viewNode:
        viewNode.SetBackgroundColor(0., 0., 0.)
        viewNode.SetBackgroundColor2(0., 0., 0.)
        viewNode.SetBoxVisible(False)
        viewNode.SetAxisLabelsVisible(False)
        viewNode.SetOrientationMarkerType(slicer.vtkMRMLAbstractViewNode.OrientationMarkerTypeAxes)

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAdded(self, caller, event, calldata):
    if slicer.mrmlScene.IsBatchProcessing():
      return
    node = calldata
    if not isinstance(node, slicer.vtkMRMLScalarVolumeNode):
      return
    self.updateParameterNodeFromVolumeNode(node)

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Enable/disable slab buttons and slider
    slabEnabled = toBool(self._parameterNode.GetParameter("SlabEnabled"))
    self.ui.SlabModeMaxRadioButton.enabled = slabEnabled
    self.ui.SlabModeMeanRadioButton.enabled = slabEnabled
    self.ui.SlabModeMinRadioButton.enabled = slabEnabled
    self.ui.SlabThicknessSliderWidget.enabled = slabEnabled

    # Update slab mode buttons
    slabModeStr = self._parameterNode.GetParameter("SlabMode") if slabEnabled else "Mean"
    getattr(self.ui, "SlabMode%sRadioButton" % slabModeStr).checked = True

    volumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")

    # Update slab slider
    spacingInMm = max(volumeNode.GetSpacing()) if volumeNode is not None else 0.0
    if slabEnabled:
      slabThicknessInMm = float(self._parameterNode.GetParameter("SlabThicknessInMm"))
    else:
      slabThicknessInMm = spacingInMm
    self.ui.SlabThicknessSliderWidget.minimum = spacingInMm
    self.ui.SlabThicknessSliderWidget.value = slabThicknessInMm

    # Update InverseGray button
    inverseGray = toBool(self._parameterNode.GetParameter("InverseGray"))
    self.ui.InverseGrayButton.checked = inverseGray

    # Update slice viewers
    QReadsLogic.setSlab(
      QReadsLogic.slabModeFromString(slabModeStr),
      QReadsLogic.slabThicknessInMmToNumberOfSlices(volumeNode, slabThicknessInMm))
    QReadsLogic.setInverseGrayEnabled(inverseGray)

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    slabEnabled = self.ui.SlabButton.checked
    self._parameterNode.SetParameter("SlabEnabled", "true" if slabEnabled else "false")
    self._parameterNode.SetParameter("SlabMode", QReadsLogic.slabModeToString(self.slabModeButtonGroup.checkedId()))
    self._parameterNode.SetParameter("SlabThicknessInMm", str(self.ui.SlabThicknessSliderWidget.value))

    self._parameterNode.SetParameter("InverseGray", "true" if self.ui.InverseGrayButton.checked else "false")

    self._parameterNode.EndModify(wasModified)

  def updateParameterNodeFromVolumeNode(self, volumeNode):
    self._parameterNode.SetParameter("SlabThicknessInMm", str(max(volumeNode.GetSpacing())))

  def onCloseApplicationButton(self):
    """
    Close application when user clicks "Close" button.
    """
    pass


#
# QReadsLogic
#

class QReadsLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  SLICEVIEW_BACKGROUND_COLORS = {
    "Red": "#18184C",
    "Yellow": "#512121",
    "Green": "#104610"
  }

  THREEDVIEW_BACKGROUND_COLORS = {
    "QReads1": "#000000",
  }

  WINDOW_LEVEL_PRESETS = {
    'CT-BodySoftTissue': (1600, -600),
    'CT-Bone': (2500, 300),
    'CT-Head': (100, 40),
    'CT-Lung': (400, 40)
  }
  """Windows level presets specified as (windows, level)"""

  SLAB_MODES = {
    vtk.VTK_IMAGE_SLAB_MAX: "Max",
    vtk.VTK_IMAGE_SLAB_MEAN: "Mean",
    vtk.VTK_IMAGE_SLAB_MIN: "Min",
    vtk.VTK_IMAGE_SLAB_SUM: "Sum"
  }
  """Slab modes supported by vtkImageReslice"""

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("SlabEnabled"):
      parameterNode.SetParameter("SlabEnabled", "false")
    if not parameterNode.GetParameter("SlabMode"):
      parameterNode.SetParameter("SlabMode", "Mean")
    if not parameterNode.GetParameter("SlabThicknessInMm"):
      parameterNode.SetParameter("SlabThicknessInMm", "1.0")
    if not parameterNode.GetParameter("InverseGray"):
      parameterNode.SetParameter("InverseGray", "false")

  @staticmethod
  def registerCustomLayout():
    customLayout = (
      "<layout type=\"vertical\">"
      " <item>"
      "  <layout type=\"horizontal\">"
      "   <item>"
      "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">"
      "     <property name=\"orientation\" action=\"default\">Axial</property>"
      "     <property name=\"viewlabel\" action=\"relayout\">B</property>"
      "     <property name=\"viewcolor\" action=\"relayout\">{Red}</property>"
      "    </view>"
      "   </item>"
      "   <item>"
      "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Yellow\">"
      "     <property name=\"orientation\" action=\"default\">Sagittal</property>"
      "     <property name=\"viewlabel\" action=\"relayout\">R</property>"
      "     <property name=\"viewcolor\" action=\"relayout\">{Yellow}</property>"
      "    </view>"
      "   </item>"
      "  </layout>"
      " </item>"
      " <item>"
      "  <layout type=\"horizontal\">"
      "   <item>"
      "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Green\">"
      "     <property name=\"orientation\" action=\"default\">Coronal</property>"
      "     <property name=\"viewlabel\" action=\"relayout\">G</property>"
      "     <property name=\"viewcolor\" action=\"relayout\">{Green}</property>"
      "    </view>"
      "   </item>"
      "   <item>"
      "    <view class=\"vtkMRMLViewNode\" singletontag=\"QReads1\">"
      "     <property name=\"viewlabel\" action=\"default\">1</property>"
      "     <property name=\"viewcolor\" action=\"default\">{QReads1}</property>"
      "    </view>"
      "   </item>"
      "  </layout>"
      " </item>"
      "</layout>").format(**QReadsLogic.SLICEVIEW_BACKGROUND_COLORS, **QReadsLogic.THREEDVIEW_BACKGROUND_COLORS)
    customLayoutId = 503
    layoutLogic = slicer.app.layoutManager().layoutLogic()
    layoutLogic.GetLayoutNode().AddLayoutDescription(customLayoutId, customLayout)
    return customLayoutId

  @staticmethod
  def setInverseGrayEnabled(enabled):
    for volumeNode in slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode"):
      if volumeNode.GetDisplayNode() is None:
        continue
      if enabled:
        colorNodeID = "vtkMRMLColorTableNodeInvertedGrey"
      else:
        colorNodeID = "vtkMRMLColorTableNodeGrey"
      volumeNode.GetDisplayNode().SetAndObserveColorNodeID(slicer.util.getNode(colorNodeID).GetID())

  def setWindowLevelPreset(self, presetName):
    for volumeNode in slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode"):
      volumeDisplayNode = volumeNode.GetDisplayNode()
      with NodeModify(volumeDisplayNode):
        volumeDisplayNode.SetAutoWindowLevel(0)
        volumeDisplayNode.SetWindowLevel(*self.WINDOW_LEVEL_PRESETS[presetName])

  @staticmethod
  def slabModeToString(slabMode):
    return QReadsLogic.SLAB_MODES[slabMode]

  @staticmethod
  def slabModeFromString(slabModeStr):
    return {v: k for k, v in QReadsLogic.SLAB_MODES.items()}[slabModeStr]

  @staticmethod
  def slabThicknessInMmToNumberOfSlices(volumeNode, tichknessInMm):
    if volumeNode is None:
      return 1
    assert tichknessInMm > 0
    return int(tichknessInMm / max(volumeNode.GetSpacing()))

  @staticmethod
  def setSlab(mode, numberOfSlices):
    assert numberOfSlices > 0
    assert mode in QReadsLogic.SLAB_MODES.keys()
    for sliceLogic in slicer.app.applicationLogic().GetSliceLogics():
      reslice = sliceLogic.GetBackgroundLayer().GetReslice()
      reslice.SetSlabMode(mode)
      reslice.SetSlabNumberOfSlices(numberOfSlices)
      sliceLogic.GetBackgroundLayer().Modified()

