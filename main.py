import sys
from PyQt5.Qt import *
from UI.mainUI import Ui_MainWindow
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
import binascii
from qsstool import QssTools
import threading


class MyThread(threading.Thread):
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        self.func(self.args)


# class AutoSendTimeVadidator(QValidator):
#     def validate(self, input_str, pos_int):
#         print(input_str, pos_int)
#         return (QValidator.Acceptable, input_str, pos_int)
#
#     def fixup(self, p_str):
#         pass


class MainUI(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.resize(500, 500)
        self.setupUi(self)
        self.UI_Init()
        self.create_signal_slot()

        QssTools.set_qss_to_obj('./UIQss.qss', self)

    def create_signal_slot(self):
        self.com.readyRead.connect(self.receive_data)

        # QPlainTextEdit
        self.pte_rx.textChanged.connect(self.pte_rx.ensureCursorVisible)
        self.pte_tx.textChanged.connect(self.pte_tx.ensureCursorVisible)

    QTextDocument
    def UI_Init(self):
        # update comx
        self.refresh_port()
        # baudrate
        self.cbox_baudrate.addItems(['300', '600', '1200', '2400', '4800', '9600', '19200', '38400', '43000',
                                     '56000', '57600', '115200', '128000'])
        self.cbox_baudrate.setCurrentText('9600')
        # parity
        self.cbox_parity.addItems(['None'])
        # databit
        self.cbox_databit.addItems(['8'])
        # stopbit
        self.cbox_stopbit.addItems(['1'])

        # port
        self.com = QSerialPort()

        # flag
        self.flag_stop_diaplay = False
        self.flag_com_on = False
        self.flag_autosend_timer = False

        self.enable_widget_COMOn(False)

        # vadidator
        # le_auto_send_time_vadi = AutoSendTimeVadidator()
        # self.le_auto_send_time.setValidator(le_auto_send_time_vadi)

    def btn_load_file_clicked(self):
        file_info = QFileDialog.getOpenFileName(self, "选择文件", "./",
                                                "All(*.*);;Python文件(*.py);;txt文件(*.txt)",
                                                "txt文件(*.txt)")
        file = open(file_info[0], 'r', encoding='utf-8')
        file_content = file.read()
        self.le_file_path.setText(file_info[0])
        self.pte_tx.insertPlainText(file_content)
        self.le_file_path.home(False)
        file.close()

    def le_time_changed(self):
        if self.le_auto_send_time.text().isdigit() == True:
            if self.flag_autosend_timer == True:
                self.killTimer(self.timer_auto_send)
                self.timer_auto_send = self.startTimer(int(self.le_auto_send_time.text()))
        else:
            QMessageBox.critical(self, "错误", "自动发送时间错误！")

    def btn_save2file(self):
        saved_data = self.pte_rx.toPlainText()

        if saved_data != '':
            file_info = QFileDialog.getOpenFileName(self, "保存文件", "./",
                                                    "All(*.*);;Python文件(*.py);;txt文件(*.txt)",
                                                    "txt文件(*.txt)")

            file = open(file_info[0], "w")
            file.write(saved_data)

    def chk_auto_send_statechanged(self):
        if self.flag_com_on == True:
            if self.chk_auto_send.isChecked() == True:
                if self.flag_autosend_timer == True:
                    self.killTimer(self.timer_auto_send)
                else:
                    self.flag_autosend_timer = True

                if self.le_auto_send_time.text().isdigit() == True:
                    self.timer_auto_send = self.startTimer(int(self.le_auto_send_time.text()))
            else:
                if self.flag_autosend_timer == True:
                    self.flag_autosend_timer = False
                    self.killTimer(self.timer_auto_send)

    def btn_stop_display(self):
        if self.btn_stop_disp.text() == "停止显示":
            self.btn_stop_disp.setText("恢复显示")
            self.flag_stop_diaplay = True
        else:
            self.btn_stop_disp.setText("停止显示")
            self.flag_stop_diaplay = False

    def btn_search_clicked(self):
        self.refresh_port()

    def btn_open_clicked(self):
        if self.btn_open.text() == "打开串口":
            self.com.setPortName(self.cbox_com.currentText())

            if self.com.open(QSerialPort.ReadWrite) == True:
                self.cbox_paras_status(False)
                self.btn_port_indict.setStyleSheet("background-color: rgb(255, 99, 52);")
                self.btn_open.setText("关闭串口")
                self.flag_com_on = True

                self.enable_widget_COMOn(True)
            else:
                self.flag_com_on = False
        else:
            self.com.close()
            self.cbox_paras_status(True)
            self.btn_port_indict.setStyleSheet("background-color: gray;")
            self.btn_open.setText("打开串口")

            self.enable_widget_COMOn(False)

    def btn_clear_clicked(self):
        self.pte_rx.clear()
        self.pte_rx.moveCursor(QTextCursor.Start)

    def btn_send_clicked(self):
        self.send_data()

    def timerEvent(self, *args, **kwargs):
        self.send_data()

    def send_data(self):
        print(self.pte_rx.textCursor().columnNumber())
        #QTextCursor
        tx_data = self.pte_tx.toPlainText()
        if len(tx_data) == 0:
            return

        if self.chkbox_tx_hex.isChecked() == False:
            self.com.write(tx_data.encode('UTF-8'))
        else:
            data = tx_data.replace(' ', '')
            if len(data) % 2 == 1:
                data = data[0:len(data) - 1]

            if data.isdigit() is False:
                QMessageBox.critical(self, "错误", "包含非十六进制数")
                return

            try:
                hex_data = binascii.a2b_hex(data)
            except:
                QMessageBox.critical(self, "错误", "转换编码错误")
                return

            try:
                self.com.write(hex_data)
            except:
                QMessageBox.critical(self, "异常", "十六进制发送错误")
                return

    def receive_data(self):
        try:
            rx_data = bytes(self.com.readAll())
        except:
            QMessageBox.critical(self, "严重错误", "串口接收数据错误！")

        if self.chkbox_rx_hex.isChecked() == False:
            try:
                if self.flag_stop_diaplay == False:
                    self.pte_rx.insertPlainText(rx_data.decode('UTF-8'))
            except:
                pass
        else:
            data = binascii.b2a_hex(rx_data).decode('ascii')
            hex_str = data + ' '
            if self.flag_stop_diaplay == False:
                self.pte_rx.insertPlainText(hex_str)

    def refresh_port(self):
        self.cbox_com.clear()
        port_list = QSerialPortInfo.availablePorts()
        for info in port_list:
            self.cbox_com.addItem(info.portName())

    def cbox_paras_status(self, status):
        self.cbox_com.setEnabled(status)
        self.cbox_baudrate.setEnabled(status)
        self.cbox_parity.setEnabled(status)
        self.cbox_databit.setEnabled(status)
        self.cbox_stopbit.setEnabled(status)
        self.btn_search.setEnabled(status)

    def enable_widget_COMOn(self, status):
        self.chk_auto_send.setEnabled(status)
        self.le_auto_send_time.setEnabled(status)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainUI()
    mainWindow.show()
    sys.exit(app.exec_())
