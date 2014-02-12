import maya.cmds as cmds
import pymel.core as pm


class UI(object):
    def __init__(self):
        title = 'curvyEdges'
        version = '1.02'

        self.ceObj = spline(self)

        if pm.window('ceWindow', exists=True):
            pm.deleteUI('ceWindow')

        with pm.window('ceWindow', title='{0} | {1}'.format(title, version), mnb=False,
                       mxb=False, sizeable=False) as window:
            with pm.columnLayout():

                # curve Frame
                with pm.frameLayout(l='Curve Settings', cll=True, cl=False, bs='out'):
                    with pm.columnLayout():
                        self.curveType = pm.radioButtonGrp(l='Curve Type:', sl=0, nrb=2, cw3=[96, 64, 128],
                                                           labelArray2=['BezierCurve', 'NurbsCurve'])
                        self.spans = pm.intSliderGrp(field=True, l='Curve Spans:', minValue=2, maxValue=24,
                                                     fieldMinValue=2, fieldMaxValue=128, value=2, cw3=[96, 64, 128])
                        with pm.rowColumnLayout(nc=2, cw=[1, 96], co=[1, 'right', 1]):
                            self.selOnly = pm.checkBox(v=False, l='Selection Only')
                            pm.button(l='Create Curve', c=self._create, width=128)

                # Deformer Frame
                with pm.frameLayout(l='Deformer Settings', bs='out', cl=False, cll=True):
                    with pm.columnLayout():
                        self.currentCrv = pm.textFieldButtonGrp(editable=False, l='Current Curve:',
                                                                bl='Select Curve', cw3=[96, 122, 64], bc=self.select)

                        self.deformers = [attrSlider(1, 0, 1, 'envelope', self.ceObj),
                                          attrSlider(1, -10, 10, 'tension', self.ceObj),
                                          attrSlider(0, 0, 256, 'dropoffDistance[0]', self.ceObj),
                                          attrSlider(1, 0, 2, 'scale[0]', self.ceObj)]

                with pm.rowColumnLayout(nc=2):
                    pm.button(l='Delete History', c=lambda *args: self.ceObj.deletHist(), w=150)
                    pm.button(l='Relink Curve', c=lambda *args: self.ceObj.reLink(), w=150)

            # Render Window
            window.show()

    def _create(self, *args):
        try:
            self.ceObj.create(self.curveType.getSelect(), self.spans.getValue(), self.selOnly.getValue())
            for i in self.deformers:
                i.setEnable(True)
                i.get()
        except:
            pass

    def select(self, *args):
        try:
            self.ceObj.select()
            for i in self.deformers:
                i.setEnable(True)
                i.get()
        except:
            self.setCurrentCurve('Select a curvyEdges curve!')
            for i in self.deformers:
                i.setEnable(False)

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

    def reLink(self):
        sel = pm.selected()
        if len(sel) == 2:
            for i in sel:
                if isinstance(i.getShape(), pm.nt.Mesh):
                    mesh = i
                elif isinstance(i.getShape(), pm.nt.CurveShape):
                    curve = i

            wire = pm.createNode('wire')
            wire.setWire(curve)
            wire.setGeometry(mesh)
            pm.select(curve, r=True)

            self.uiObj.select()

        else:
            pm.warning('Must select a polyObject and a Curve to relink!')


class attrSlider(object):
    def __init__(self, value, min, max, name, ceObj):
        self.value = value
        self.min = min
        self.max = max
        self.name = name
        self.ceObj = ceObj
        self.attr = pm.floatSliderGrp(field=True, l=self.name, value=self.value, pre=3, enable=False,
                                      minValue=self.min, maxValue=self.max, dc=self.set, cc=self.set, cw3=[96, 64, 128])

    def get(self):
        try:
            value = getattr(self.ceObj.wire[0], self.name).get(self.attr.getValue())
            self.attr.setValue(value)
        except:
            AttributeError('{0} node does not exist'.format(self.ceObj.wire[0]))

    def set(self, *args):
        try:
            getattr(self.ceObj.wire[0], self.name).set(self.attr.getValue())
        except:
            AttributeError('{0} node does no longer exist'.format(self.ceObj.wire[0]))

    def setEnable(self, val):
        self.attr.setEnable(val)
