import maya.cmds as cmds
import pymel.core as pm


class UI(object):
    def __init__(self):
        title = 'curvyEdges'
        version = '1.03'

        self.ceObj = spline(self)

        if pm.window('curvyEdgesWin', exists=True):
            pm.deleteUI('curvyEdgesWin')

        with pm.window('curvyEdgesWin', title='{0} | {1}'.format(title, version),
                       mnb=False, mxb=False, sizeable=False) as window:
            with pm.columnLayout():

                # curve Frame
                with pm.frameLayout(l='Curve Settings', cll=True, cl=False, bs='out'):
                    with pm.columnLayout():
                        self.curveType = pm.radioButtonGrp(l='Curve Type:', sl=0, nrb=2, cw3=[96, 96, 128],
                                                           labelArray2=['BezierCurve', 'NurbsCurve'])
                        self.spans = pm.intSliderGrp(field=True, l='Curve Spans:', minValue=2, maxValue=24,
                                                     fieldMinValue=2, fieldMaxValue=128, value=2, cw3=[96, 64, 128])
                        with pm.rowColumnLayout(nc=2, cw=[1, 96], co=[1, 'right', 1]):
                            self.selOnly = pm.checkBox(v=False, l='Selection Only')
                            pm.button(l='Create Curve', c=self._create, width=201)

                # Deformer Frame
                with pm.frameLayout(l='Deformer Settings', bs='out', cl=False, cll=True):
                    with pm.columnLayout():
                        self.currentCrv = pm.textFieldGrp(editable=False, l='Current Curve:', cw2=[96, 195])

                        self.deformers = [attrSlider(1, 0, 1, 'envelope', self.ceObj),
                                          attrSlider(1, -10, 10, 'tension', self.ceObj),
                                          attrSlider(0, 0, 256, 'dropoffDistance[0]', self.ceObj),
                                          attrSlider(1, 0, 2, 'scale[0]', self.ceObj)]

            window.show()
            pm.scriptJob(event=['SelectionChanged', self.select], protected=True, p=window)
            self.select()

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

    def select(self):
        sel = pm.selected()
        if isinstance(sel[0], pm.nt.Transform):
            if not isinstance(sel[0].getShape(), pm.nt.NurbsCurve):
                raise Exception('Invalid Selection Type')

        elif isinstance(sel[0], pm.NurbsCurveCV):
            sel = [i.node().getParent() for i in sel]

        else:
            raise Exception('Invalid Selection Type')

        self.wire = pm.listConnections(sel[0].getShape())
        self.uiObj.setCurrentCurve(sel[0].shortName())


class attrSlider(object):
    def __init__(self, value, min, max, name, ceObj):
        self.value = value
        self.min = min
        self.max = max
        self.name = name
        self.ceObj = ceObj

        self.undoState = False
        self.attr = pm.floatSliderGrp(field=True, l=self.name, value=self.value, pre=3, enable=False,
                                      minValue=self.min, maxValue=self.max, dc=self.set,
                                      cc=self.closeChunk, cw3=[96, 64, 128])

        pm.scriptJob(event=['Undo', self.get], protected=True, p=self.attr)

    def get(self):
        try:
            value = getattr(self.ceObj.wire[0], self.name).get(self.attr.getValue())
            self.attr.setValue(value)
        except:
            AttributeError('{0} node does not exist'.format(self.ceObj.wire[0]))

    def set(self, *args):
        if not self.undoState:
            self.undoState = True
            pm.undoInfo(openChunk=True)

        try:
            getattr(self.ceObj.wire[0], self.name).set(self.attr.getValue())
        except:
            AttributeError('{0} node does no longer exist'.format(self.ceObj.wire[0]))

    def closeChunk(self, *args):
        if self.undoState:
            pm.undoInfo(closeChunk=True)
            self.undoState = False

    def setEnable(self, val):
        self.attr.setEnable(val)
