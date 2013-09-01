import maya.cmds as cmds
import pymel.core as pm


class UI(object):
    def __init__(self):
        title = 'curvyEdges'
        version = '1.00'

        self.ceObj = spline(self)

        if pm.window('ceWindow', exists=True):
            pm.deleteUI('ceWindow')

        with pm.window('ceWindow', title=title + ' | ' + version, mb=True, mbv=True, mnb=False,
                       mxb=False, nm=2, sizeable=False) as window:
            with pm.columnLayout():

                # curve Frame
                with pm.frameLayout(l='Curve Settings', cll=True, cl=False, bs='out',
                                    w=402, mh=10):
                    with pm.columnLayout(co=['both', 10]):
                        self.curveType = pm.radioButtonGrp(l='Curve Type:', sl=0, nrb=2,
                                                           labelArray2=['BezierCurve', 'NurbsCurve'])
                        self.spans = pm.intSliderGrp(field=True, l='Curve Spans:', minValue=2, maxValue=24,
                                                     fieldMinValue=2, fieldMaxValue=128, value=2)
                        with pm.rowColumnLayout(nc=2):
                            self.selOnly = pm.checkBox(v=False, l='Affect Selection Only')
                            # Create Curve
                            pm.button(l='Create Curve', c=self._create, width=262)

                # Deformer Frame
                with pm.frameLayout(l='Deformer Settings', bs='out', w=402, mh=10, cl=False, cll=True):
                    with pm.columnLayout():
                        self.currentCrv = pm.textFieldButtonGrp(editable=False, l='Current Curve:',
                                                                bl='Select Curve', cw=[2, 170], bc=self._select)

                        self.deformers = [attrSlider(1, 0, 1, 'envelope', self.ceObj),
                                          attrSlider(1, -10, 10, 'tension', self.ceObj),
                                          attrSlider(0, 0, 256, 'dropoffDistance[0]', self.ceObj),
                                          attrSlider(1, 0, 2, 'scale[0]', self.ceObj)]

                with pm.rowColumnLayout(nc=1, cw=[(1, 402)]):
                    pm.button(l='Delete History', c=self._deleteHist)

            # Render Window
            window.show()

    def _create(self, *args):
        try:
            self.ceObj.create(self.curveType.getSelect(), self.spans.getValue(), self.selOnly.getValue())
            for i in self.deformers:
                i.setEnable()
                i.get()
        except:
            pass

    def _select(self, *args):
        try:
            self.ceObj.select()
            for i in self.deformers:
                i.setEnable()
                i.get()
        except:
            self.setCurrentCurve('Select a curvyEdges curve!')
            for i in self.deformers:
                i.setDisable()

    def _deleteHist(self, *args):
        self.ceObj.deletHist()

    def setCurrentCurve(self, curve):
        self.currentCrv.setText(curve)


class spline(object):
    def __init__(self, uiObj):
        self.uiObj = uiObj

    def create(self, curveType, spans, selOnly):
        sel = pm.selected()
        cmds.CreateCurveFromPoly()
        curve = pm.selected()
        pm.rebuildCurve(curve, spans=spans)
        # set UI curve
        self.uiObj.setCurrentCurve(curve[0].shortName())

        if curveType == 1:
            pm.nurbsCurveToBezier()
        pm.delete(curve, ch=True)

        # Deform
        if selOnly:
            sel = pm.polyListComponentConversion(sel, fe=True, tv=True)
            self.wire = pm.wire(sel, w=curve)
        else:
            #Object
            self.wire = pm.wire(sel[0].node(), w=curve)

    def deletHist(self):
        sel = pm.selected()
        pm.delete(sel[0].getShape(), ch=True)

    def select(self):
        sel = pm.selected()
        self.wire = pm.listConnections(sel[0].getShape())
        self.uiObj.setCurrentCurve(sel[0].shortName())


class attrSlider(object):
    def __init__(self, value, min, max, name, ceObj):
        self.value = value
        self.min = min
        self.max = max
        self.name = name
        self.ceObj = ceObj
        self.attr = pm.floatSliderGrp(field=True, l=self.name, value=self.value, pre=3, enable=False,
                                      minValue=self.min, maxValue=self.max, dc=self.set, cc=self.set)

    def get(self):
        value = getattr(self.ceObj.wire[0], self.name).get(self.attr.getValue())
        self.attr.setValue(value)

    def set(self, *args):
        getattr(self.ceObj.wire[0], self.name).set(self.attr.getValue())

    def setEnable(self):
        self.attr.setEnable(True)

    def setDisable(self):
        self.attr.setEnable(False)
