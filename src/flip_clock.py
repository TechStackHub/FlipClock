# flip_clock.py (PySide6) - resizable, no shadow, context menu pin/unpin
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QObject, Signal, QRect
from PySide6.QtGui import QPainter, QFont, QColor, QPen, QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QSizePolicy, QMenu
from datetime import datetime
from math import cos, radians
import sys

CARD = QColor("#FFFFFF")
TEXT = QColor("#111827")

def clamp(v, lo, hi): return max(lo, min(hi, v))

class FlipAnimator(QObject):
    changed = Signal(); finished = Signal()
    def __init__(self, duration=350, parent=None):
        super().__init__(parent)
        self._angle=0.0; self._active=False; self._duration=max(1,duration)
        self._easing = QEasingCurve(QEasingCurve.InOutCubic)
        self._t = 0; self._timer = QTimer(self); self._timer.timeout.connect(self._step)
        self._timer.setInterval(1000//60)
    def start(self):
        if self._active: return
        self._active=True; self._t=0; self._angle=0.0; self._timer.start()
    def _step(self):
        self._t += self._timer.interval()
        p = clamp(self._t / self._duration, 0.0, 1.0)
        self._angle = 180.0 * self._easing.valueForProgress(p)
        self.changed.emit()
        if p>=1.0: self._timer.stop(); self._active=False; self.finished.emit()
    def isActive(self): return self._active
    @property
    def angle(self): return self._angle

class FlipDigit(QWidget):
    def __init__(self, value=0, base_font=140, base_w=180, base_h=240, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.value=value%10; self.next_value=self.value
        self.anim=FlipAnimator(420,self); self.anim.changed.connect(self.update); self.anim.finished.connect(self._on_finished)
        self.font_family='Segoe UI'; self.base_font=base_font; self.base_w=base_w; self.base_h=base_h
        self._radius=22; self._padding=22; self._split_ratio=0.52; self.scale=1.0
        self._rebuild_font(); self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed); self._apply_size()
    def set_scale(self,s:float):
        self.scale=float(max(0.5,min(3.0,s))); self._rebuild_font(); self._apply_size(); self.update()
    def _rebuild_font(self):
        self.font = QFont(self.font_family); self.font.setPointSizeF(self.base_font*self.scale); self.font.setWeight(QFont.Black)
    def _apply_size(self):
        self.setFixedSize(int(self.base_w*self.scale), int(self.base_h*self.scale))
    def startFlipTo(self, next_value:int):
        next_value%=10
        if next_value==self.value or self.anim.isActive(): self.next_value=next_value; return
        self.next_value=next_value; self.anim.start()
    def _on_finished(self): self.value=self.next_value; self.update()
    def paintEvent(self, e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing); r=self.rect()
        p.setPen(Qt.NoPen); p.setBrush(CARD); rad=int(22*self.scale); p.drawRoundedRect(r.adjusted(0,0,-4,-4), rad, rad)
        split_y = int(r.height()*self._split_ratio)
        p.setPen(QPen(QColor(0,0,0,30), max(1,int(1*self.scale)))); p.drawLine(r.left()+int(12*self.scale), split_y, r.right()-int(16*self.scale), split_y)
        p.setPen(TEXT); p.setFont(self.font)
        pad=int(22*self.scale); top=r.adjusted(pad,pad,-pad-4,-(r.height()-split_y)); bottom=r.adjusted(pad,split_y,-pad-4,-pad-4)
        cur=f"{self.value}"; nxt=f"{self.next_value}"; ang=self.anim.angle if self.anim.isActive() else 0.0
        def draw_text(rr,t): p.drawText(rr, Qt.AlignCenter, t)
        if not self.anim.isActive():
            p.setClipRect(top); draw_text(r,cur); p.setClipping(False); p.setClipRect(bottom); draw_text(r,cur); p.setClipping(False); return
        if ang<=90:
            p.setClipRect(top); p.save(); cx=r.center().x(); cy=top.center().y(); p.translate(cx,cy); p.scale(1.0, abs(cos(radians(ang)))); p.translate(-cx,-cy); draw_text(r,cur); p.restore(); p.setClipping(False)
            p.setClipRect(bottom); draw_text(r,cur); p.setClipping(False)
        else:
            p.setClipRect(top); draw_text(r,nxt); p.setClipping(False)
            p.setClipRect(bottom); p.save(); cx=r.center().x(); cy=bottom.center().y(); p.translate(cx,cy); p.scale(1.0, abs(cos(radians(180-ang)))); p.translate(-cx,-cy); draw_text(r,nxt); p.restore(); p.setClipping(False)

class Colon(QWidget):
    def __init__(self, base_w=30, parent=None):
        super().__init__(parent); self.base_w=base_w; self.scale=1.0; self.setFixedWidth(int(self.base_w*self.scale)); self._on=True
        self.timer=QTimer(self); self.timer.timeout.connect(self._toggle); self.timer.start(500)
    def set_scale(self,s:float): self.scale=float(max(0.5,min(3.0,s))); self.setFixedWidth(int(self.base_w*self.scale)); self.update()
    def _toggle(self): self._on=not self._on; self.update()
    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing); p.setPen(Qt.NoPen); c=TEXT if self._on else QColor(0,0,0,60); p.setBrush(c)
        w,h=self.width(), self.height(); rr=max(4,int(min(w,h)//14+4*self.scale)); y1,y2=int(h*0.38),int(h*0.62); x=w//2; p.drawEllipse(x-rr,y1-rr,2*rr,2*rr); p.drawEllipse(x-rr,y2-rr,2*rr,2*rr)

class FlipClock(QWidget):
    def __init__(self, use_24h=True, parent=None):
        super().__init__(parent); self.use_24h=use_24h
        self.setAttribute(Qt.WA_TranslucentBackground, True); self.setWindowFlag(Qt.FramelessWindowHint, True); self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setStyleSheet('background: transparent;'); self._scale=1.0
        self.layout=QHBoxLayout(self); self.layout.setContentsMargins(20,20,20,20); self.layout.setSpacing(20)
        self.digits=[FlipDigit(0) for _ in range(6)]; self.colon1=Colon(); self.colon2=Colon()
        self.layout.addWidget(self.digits[0]); self.layout.addWidget(self.digits[1]); self.layout.addWidget(self.colon1)
        self.layout.addWidget(self.digits[2]); self.layout.addWidget(self.digits[3]); self.layout.addWidget(self.colon2)
        self.layout.addWidget(self.digits[4]); self.layout.addWidget(self.digits[5])
        self._dragging=False; self._resizing=False; self._resize_margin=24
        self.setContextMenuPolicy(Qt.CustomContextMenu); self.customContextMenuRequested.connect(self._show_menu)
        self.addAction(self._act('Increase size','Ctrl+=', lambda: self.set_scale(self._scale*1.1)))
        self.addAction(self._act('Decrease size','Ctrl+-', lambda: self.set_scale(self._scale/1.1)))
        self.addAction(self._act('Reset size','Ctrl+0', lambda: self.set_scale(1.0)))
        self._init_time(); self.timer=QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(1000)
    def _act(self,t,s,cb): a=QAction(t,self); a.setShortcut(QKeySequence(s)); a.triggered.connect(cb); return a
    def _show_menu(self,pos):
        m=QMenu(self); pin = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        a1=QAction('Unpin (disable always-on-top)' if pin else 'Pin (always on top)', self); a1.triggered.connect(self.toggle_pin); m.addAction(a1)
        size = m.addMenu('Size')
        for label,f in [('Small (80%)',0.8),('Medium (100%)',1.0),('Large (120%)',1.2),('XL (150%)',1.5),('XXL (200%)',2.0)]:
            act=QAction(label,self); act.triggered.connect(lambda _,ff=f: self.set_scale(ff)); size.addAction(act)
        m.addSeparator(); a2=QAction('Exit',self); a2.triggered.connect(self.close); m.addAction(a2); m.exec(self.mapToGlobal(pos))
    def toggle_pin(self):
        pin = bool(self.windowFlags() & Qt.WindowStaysOnTopHint); self.setWindowFlag(Qt.WindowStaysOnTopHint, not pin); self.show()
    def set_scale(self,s:float):
        self._scale=float(max(0.5,min(3.0,s)))
        for d in self.digits: d.set_scale(self._scale)
        self.colon1.set_scale(self._scale); self.colon2.set_scale(self._scale)
        pad=int(20*self._scale); self.layout.setContentsMargins(pad,pad,pad,pad); self.layout.setSpacing(int(20*self._scale))
        self.adjustSize(); center=self.frameGeometry().center(); self.move(center - self.rect().center()); self.update()
    def _init_time(self):
        now=datetime.now(); h=now.hour; h=(h if self.use_24h else ((h%12) or 12)); m,s=now.minute,now.second; ds=f"{h:02d}{m:02d}{s:02d}"
        for i,d in enumerate(ds): self.digits[i].value=int(d); self.digits[i].next_value=int(d); self.digits[i].update()
    def _tick(self):
        now=datetime.now(); h=now.hour; h=(h if self.use_24h else ((h%12) or 12)); m,s=now.minute,now.second; ds=[int(x) for x in f"{h:02d}{m:02d}{s:02d}"]
        for i,d in enumerate(ds):
            if d!=self.digits[i].value: self.digits[i].startFlipTo(d)
    def mousePressEvent(self,e):
        if e.button()==Qt.LeftButton:
            if self._in_resize_corner(e.pos()):
                self._resizing=True; self._start_rect=self.geometry(); self._start_pos=e.globalPosition().toPoint()
            else:
                self._dragging=True; self._drag_offset=e.globalPosition().toPoint()-self.frameGeometry().topLeft(); e.accept()
    def mouseMoveEvent(self,e):
        if self._resizing:
            delta=e.globalPosition().toPoint()-self._start_pos; new_w=max(200, self._start_rect.width()+delta.x()); factor=new_w/self._start_rect.width()
            self.set_scale(self._scale*factor); self._start_rect=self.geometry(); self._start_pos=e.globalPosition().toPoint(); e.accept()
        elif self._dragging:
            self.move(e.globalPosition().toPoint()-self._drag_offset); e.accept()
        else:
            self.setCursor(Qt.SizeFDiagCursor if self._in_resize_corner(e.pos()) else Qt.ArrowCursor)
    def mouseReleaseEvent(self,e): self._dragging=False; self._resizing=False; self.setCursor(Qt.ArrowCursor)
    def _in_resize_corner(self,pos):
        r=self.rect(); margin=24; return (pos.x()>=r.right()-margin and pos.y()>=r.bottom()-margin)

def main():
    app=QApplication(sys.argv); w=FlipClock(use_24h=True); w.set_scale(1.2); w.adjustSize()
    screen=app.primaryScreen().geometry(); w.move(screen.center()-w.rect().center()); w.show(); sys.exit(app.exec())

if __name__=='__main__': main()
