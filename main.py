from uidesign import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QApplication, \
QFileDialog, QInputDialog
from PyQt5.QtGui import QCloseEvent
import sys
import sqlite3 as lite
from random import randint
from itertools import groupby
import shutil


class MyWin(QtWidgets.QMainWindow):


    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow() # Экземпляр класса Ui_MainWindow, в нем конструктор всего GUI.
        self.ui.setupUi(self) # Инициализация GUI
        self.ui.checkBox_2.clicked.connect(self.setMaterial) # Фильтр по материалу
        self.ui.checkBox_3.clicked.connect(self.setPressure) # Фильтр по номинальному давлению
        self.ui.checkBox_4.clicked.connect(self.setWorkspace) # Фильтр по рабочей среде
        self.ui.checkBox_5.clicked.connect(self.setTempretureFrom) # Фильтр по т.о.с. (ОТ)
        self.ui.checkBox_6.clicked.connect(self.setTempretureTo) # Фильтр по т.о.с. (ДО)
        self.ui.checkBox_7.clicked.connect(self.setTypeConnection) # Фильтр по типу присоединения
        self.ui.checkBox_8.clicked.connect(self.setConnectionSizes) # Фильтр по присоединительным размерам
        self.ui.checkBox_9.clicked.connect(self.setWeight) # Фильтр по весу
        self.ui.checkBox.clicked.connect(self.stopReadOnly) # Если чекбокс активирован, вкл. редактирование листбоксов.
        self.ui.pushButton.clicked.connect(self.addRow) # Добавить запись в бд + таблицу.
        self.ui.pushButton_2.clicked.connect(self.saveChanges) # Сохранять изменения для записей.
        self.ui.pushButton_3.clicked.connect(self.confirmDeleteRow) # Удалить запись
        self.ui.pushButton_7.clicked.connect(self.changeImage) # Изменить картинку для клапана.
        self.ui.pushButton_5.clicked.connect(self.authOn) # Вход для суперюзера.
        self.ui.pushButton_6.clicked.connect(self.authOff) # Вход для суперюзера.
        self.ui.pushButton_8.clicked.connect(self.openDb) # Создать подключение к БД.
        self.ui.pushButton_9.clicked.connect(self.createBackUp) # Создать бэкап БД
        self.ui.pushButton_19.clicked.connect(self.mybutton_clicked) #
        self.ui.listWidget.itemClicked.connect(self.fillText)  # Выбранный итем листбокса.

    def initRows(self):
        """ Устанавливает количество строк в таблице, исходя
            из данных в бд"""

        self.ui.tableWidget.setRowCount(len(self.connecting()))

    def connecting(self):
        """ Возвращает список кортежей записей """

        conn = lite.connect(db_)
        cursor = conn.execute("SELECT * FROM valve")
        results = cursor.fetchall()
        conn.close()

        return results

    def billRows(self):
        """ Заполнение записей в таблице """

        getRes = self.connecting() # Collecting results
        row = 0
        columnsCount = [x for x in range(0, 11)] # 11 columns (0-10 ind.)
        for i in range(len(self.connecting())):
            for item in columnsCount:
                self.ui.tableWidget.setItem(row, item,
                        QTableWidgetItem(getRes[row][columnsCount[item]]))
            row += 1

    def clearGroupBox(self):
        """ Очистка всех полей после удаления записи из бд. """

        self.ui.lineEdit.clear()
        self.ui.lineEdit_2.clear()
        self.ui.lineEdit_3.clear()
        self.ui.lineEdit_4.clear()
        self.ui.lineEdit_5.clear()
        self.ui.lineEdit_20.clear()
        self.ui.lineEdit_6.clear()
        self.ui.lineEdit_7.clear()
        self.ui.textEdit.clear()
        self.ui.lineEdit_8.clear()
        self.ui.lineEdit_9.clear()

    def clearGroupBox2(self):
        """ Очистка текстовых полей после добавления записи в бд. """

        self.ui.lineEdit_10.clear()
        self.ui.lineEdit_11.clear()
        self.ui.lineEdit_12.clear()
        self.ui.lineEdit_13.clear()
        self.ui.lineEdit_14.clear()
        self.ui.lineEdit_15.clear()
        self.ui.lineEdit_16.clear()
        self.ui.lineEdit_17.clear()
        self.ui.textEdit_2.clear()
        self.ui.lineEdit_18.clear()
        self.ui.lineEdit_19.clear()

    def addRow(self):
        """ Добавить запись в бд и в таблицу"""

        mark = self.ui.lineEdit_10.text()
        material = self.ui.lineEdit_11.text()
        pressure = self.ui.lineEdit_12.text()
        workspace = self.ui.lineEdit_13.text()
        temperature_from = self.ui.lineEdit_14.text()
        temperature_to = self.ui.lineEdit_15.text()
        pipeline_con = self.ui.lineEdit_16.text()
        demensual_con = self.ui.lineEdit_17.text()
        purpose = self.ui.textEdit_2.toPlainText()
        oper_cond = self.ui.lineEdit_18.text()
        weight = self.ui.lineEdit_19.text()

        con = lite.connect(db_)
        with con:
            cur = con.cursor()
            sql = ''' INSERT INTO valve (mark, material, pressure, workspace,
                    temperature_from, temperature_to,
                    pipeline_con, demensual_con, purpose, oper_cond, weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
            cur.execute(sql, (mark, material, pressure, workspace,
                              temperature_from, temperature_to, pipeline_con,
                              demensual_con, purpose, oper_cond, weight))
        con.close()
        self.initRows()
        self.billRows()
        self.clearGroupBox2()
        self.ui.listWidget.addItem(mark)
        self.comboMaterial()
        self.comboWorkspace()
        self.comboTypeConnection()
        self.comboConnectionSize()
        QMessageBox.information(self, "Уведомление",
                                "Запись успешно добавлена.",
                                QMessageBox.Ok)

    def addItemList(self):
        """ Заполнить листбокс марками клапанов из полей бд"""

        self.ui.listWidget.clear()
        res = self.connecting()
        for i in range(len(res)):
            self.ui.listWidget.addItem(res[i][0])

    def fillText(self, item):
        """ Заполнение полей по выбранному итему листбокса """

        con = lite.connect(db_)
        mark = item.text()
        with con:
            cur = con.cursor()
            sql = ''' SELECT * FROM valve 
                WHERE mark = ? '''
            cur.execute(sql, (mark,))
            res = cur.fetchall()
        con.close()

        self.ui.lineEdit.setText(res[0][0])
        self.ui.lineEdit_2.setText(res[0][1])
        self.ui.lineEdit_3.setText(res[0][2])
        self.ui.lineEdit_4.setText(res[0][3])
        self.ui.lineEdit_5.setText(res[0][4])
        self.ui.lineEdit_20.setText(res[0][5])
        self.ui.lineEdit_6.setText(res[0][6])
        self.ui.lineEdit_7.setText(res[0][7])
        self.ui.textEdit.setText(res[0][8])
        self.ui.lineEdit_8.setText(res[0][9])
        self.ui.lineEdit_9.setText(res[0][10])

        global id_
        id_ = res[0][12]

        global namedMark
        namedMark = item.text()

    def stopReadOnly(self):
        """ Позволяет редактировать поля характеристик клапана"""

        if self.ui.checkBox.isChecked():
            self.ui.lineEdit.setReadOnly(False)
            self.ui.lineEdit_2.setReadOnly(False)
            self.ui.lineEdit_3.setReadOnly(False)
            self.ui.lineEdit_4.setReadOnly(False)
            self.ui.lineEdit_5.setReadOnly(False)
            self.ui.lineEdit_20.setReadOnly(False)
            self.ui.lineEdit_6.setReadOnly(False)
            self.ui.lineEdit_7.setReadOnly(False)
            self.ui.lineEdit_8.setReadOnly(False)
            self.ui.lineEdit_9.setReadOnly(False)
            self.ui.textEdit.setReadOnly(False)
            self.ui.pushButton_2.setDisabled(False)
            self.ui.pushButton_3.setDisabled(False)
            self.ui.pushButton_7.setDisabled(False)
            self.ui.groupBox_2.setDisabled(False)
        else:
            self.ui.lineEdit.setReadOnly(True)
            self.ui.lineEdit_2.setReadOnly(True)
            self.ui.lineEdit_3.setReadOnly(True)
            self.ui.lineEdit_4.setReadOnly(True)
            self.ui.lineEdit_5.setReadOnly(True)
            self.ui.lineEdit_20.setReadOnly(True)
            self.ui.lineEdit_6.setReadOnly(True)
            self.ui.lineEdit_7.setReadOnly(True)
            self.ui.lineEdit_8.setReadOnly(True)
            self.ui.lineEdit_9.setReadOnly(True)
            self.ui.textEdit.setReadOnly(True)
            self.ui.pushButton_2.setDisabled(True)
            self.ui.pushButton_3.setDisabled(True)
            self.ui.pushButton_7.setDisabled(True)
            self.ui.groupBox_2.setDisabled(True)

    def saveChanges(self):
        """ Обновляет данные записи """

        con = lite.connect(db_)
        with con:
            cur = con.cursor()
            sql = """UPDATE valve
                SET mark = ?, material = ?, pressure = ?, workspace = ?,
                temperature_from = ?, temperature_to = ?,
                pipeline_con = ?, demensual_con = ?, purpose = ?, 
                oper_cond = ?, weight = ?
                WHERE id = ?"""
            cur.execute(sql, (self.ui.lineEdit.text(),
                              self.ui.lineEdit_2.text(),
                              self.ui.lineEdit_3.text(),
                              self.ui.lineEdit_4.text(),
                              self.ui.lineEdit_5.text(),
                              self.ui.lineEdit_20.text(),
                              self.ui.lineEdit_6.text(),
                              self.ui.lineEdit_7.text(),
                              self.ui.textEdit.toPlainText(),
                              self.ui.lineEdit_8.text(),
                              self.ui.lineEdit_9.text(), id_))
        con.close()
        self.initRows()
        self.billRows()
        self.addItemList()
        self.msgSave()
        self.comboMaterial()
        self.comboWorkspace()
        self.comboTypeConnection()
        self.comboConnectionSize()

    def confirmDeleteRow(self):
        """ Подтверждение удаления записи,
         но окончательное удаление в функции lastConfirmDelete """

        if self.ui.listWidget.currentRow() == -1:
            QMessageBox.information(self, "Уведомление",
                                    "Сначала выберите запись.",
                                    QMessageBox.Ok);
        else:
            answer = QMessageBox.question(self, "Подтвердите действие",
                                         "Вы действительно хотите удалить запись?");
            if answer == QMessageBox.Yes:
                self.lastConfirmDelete();

    def lastConfirmDelete(self):
        """ Ввод рандомного числа для
        окончательного подтверждения удаления """

        rand = randint(1, 10)
        text, ok = QInputDialog.getText(self, 'Подтверждение',
                                        'Введите следующее число: {}'.format(rand));
        if ok:
            if int(text) == rand:
                con = lite.connect(db_)
                with con:
                    cur = con.cursor()
                    sql = """ DELETE FROM valve
                                        WHERE id = ? """
                    cur.execute(sql, (id_,))
                con.close()
                self.initRows()
                self.billRows()
                self.ui.listWidget.takeItem(self.ui.listWidget.currentRow())
                self.clearGroupBox()
                self.comboMaterial()
                self.comboWorkspace()
                self.comboTypeConnection()
                self.comboConnectionSize()
                QMessageBox.information(self, "Подтверждение",
                                        "Запись удалена",
                                        QMessageBox.Ok)
            else:
                return self.lastConfirmDelete()

    def msgSave(self):
        """ messageBox об успешном изменении сохранений """

        QMessageBox.information(self, "Уведомление",
                                "Изменения успешно сохранены.",
                                QMessageBox.Ok)

    def authOn(self):
        """ Администраторские права ползволяют изменять БД. """

        if self.ui.lineEdit_21.text() == " " \
                and self.ui.lineEdit_22.text() == " ":
            self.ui.checkBox.setDisabled(False)
            self.ui.lineEdit_21.clear()
            self.ui.lineEdit_22.clear()
            QMessageBox.information(self, "Уведомление",
                                    "Режим администрирования включен.",
                                    QMessageBox.Ok)
            self.setWindowTitle("Взаимодействие с БД. [SUPER USER]")
        else:
            QMessageBox.information(self, "Уведомление",
                                    "Такой пользователь не найден.",
                                    QMessageBox.Ok)
            self.ui.lineEdit_21.clear()
            self.ui.lineEdit_22.clear()

    def authOff(self):
        """ Выход из режима администрирования. """

        self.ui.checkBox.setChecked(False)
        self.ui.checkBox.setDisabled(True)
        self.stopReadOnly()
        QMessageBox.information(self, "Уведомление",
                                "Вы перешли в режим просмотра.",
                                QMessageBox.Ok)
        self.setWindowTitle("Взаимодействие с БД. [NORMAL USER]")

    def mybutton_clicked(self):
        """ Поиск по фильтру """

        results = [] # Для хранения подходящих названий марок.

        resy = self.connecting() # Массив картежей с клапанами.

        for i in resy:
            boolRes = True  # Для определения истинности вхождений.

            print(i)

            if self.ui.checkBox_2.isChecked():
                material = self.ui.comboBox.currentText()
                if i[1] == material:
                    boolRes = True
                else:
                    boolRes = False

            if self.ui.checkBox_3.isChecked():
                if boolRes:
                    pressure = float(self.ui.lineEdit_26.text().replace(',', '.')) # Input number
                    getFloatPressure = float(i[2].replace(',', '.')) # Number from DB
                    if pressure > getFloatPressure:
                        boolRes = True
                    else:
                        boolRes = False

            if self.ui.checkBox_4.isChecked():
                if boolRes:
                    workspace_ = self.ui.comboBox_3.currentText()
                    if i[3] == workspace_:
                        boolRes = True
                    else:
                        boolRes = False

            if self.ui.checkBox_5.isChecked():
                if boolRes:
                    tempFrom = float(self.ui.lineEdit_23.text().replace(',', '.')) # Input number
                    getFloatTempFrom = float(i[4].replace(',', '.')) # Number from DB
                    if tempFrom > getFloatTempFrom:
                        boolRes = True
                    else:
                        boolRes = False

            if self.ui.checkBox_6.isChecked():
                if boolRes:
                    tempTo = float(self.ui.lineEdit_24.text().replace(',', '.')) # Input number
                    getFloatTempTo = float(i[5].replace(',', '.'))  # Number from DB
                    if tempTo < getFloatTempTo:
                        boolRes = True
                    else:
                        boolRes = False

            if self.ui.checkBox_7.isChecked():
                if boolRes:
                    conType = self.ui.comboBox_6.currentText()
                    if i[6] == conType:
                        boolRes = True
                    else:
                        boolRes = False

            if self.ui.checkBox_8.isChecked():
                if boolRes:
                    conSizes = self.ui.comboBox_17.currentText()
                    if i[7] == conSizes:
                        boolRes = True
                    else:
                        boolRes = False

            if self.ui.checkBox_9.isChecked():
                if boolRes:
                    getWeight = float(self.ui.lineEdit_25.text().replace(',', '.')) # Input number
                    print(getWeight)
                    getFloatWeight = float(i[10].replace(',', '.'))  # Number from DB
                    print(getFloatWeight)
                    if getWeight > getFloatWeight:
                        boolRes = True
                    else:
                        boolRes = False

            print(boolRes)

            if boolRes:
                results.append(i[0])

            boolRes = True

        print(results,"\n")

    # def closeEvent(self, event):
    #     """ Выход из приложения """
    #
    #     reply = QMessageBox.question(self, "Выход",
    #                                  "Вы уверены, что хотите выйти?",
    #                                  QMessageBox.Yes, QMessageBox.No)
    #     event.accept() if reply == QMessageBox.Yes else event.ignore()

    def comboMaterial(self):
        """ Заполнение comboBox материалов """

        results = self.connecting() # Массив кортежей записей
        res = [] # Пустой массив для хранения неповторяющихся элементов
        for i in range(len(results)): # Цикл, проходящий len(results) раз
            res.append(results[i][1]) # Добавить в массив материал
        res = [el for el, _ in groupby(res)] # Убрать повторяющиеся названия
        self.ui.comboBox.clear() # Очистить comboBox
        self.ui.comboBox.addItems(res) # Заполнить comboBox массивом res

    def comboWorkspace(self):
        """ Заполнение comboBox рабочей среды """

        results = self.connecting()
        res = []
        for i in range(len(results)):
            res.append(results[i][3])
            res = [el for el, _ in groupby(res)]
            self.ui.comboBox_3.clear()
            self.ui.comboBox_3.addItems(res)

    def comboTypeConnection(self):
        """ Заполнение comboBox типа присоединения """

        results = self.connecting()
        res = []
        for i in range(len(results)):
            res.append(results[i][6])
            res = [el for el, _ in groupby(res)]
            self.ui.comboBox_6.clear()
            self.ui.comboBox_6.addItems(res)

    def comboConnectionSize(self):
        """ Заполнение comboBox присоединительных размеров """

        results = self.connecting()
        res = []
        for i in range(len(results)):
            res.append(results[i][7])
            res = [el for el, _ in groupby(res)]
            self.ui.comboBox_17.clear()
            self.ui.comboBox_17.addItems(res)

    def setMaterial(self):
        """ Фильтр по материалу """

        if self.ui.checkBox_2.isChecked() == True:
            self.ui.comboBox.setDisabled(False)
        else:
            self.ui.comboBox.setDisabled(True)

    def setPressure(self):
        """ Фильтр по номинальному давлению """

        if self.ui.checkBox_3.isChecked() == True:
            self.ui.lineEdit_26.setDisabled(False)
        else:
            self.ui.lineEdit_26.setDisabled(True)

    def setWorkspace(self):
        """ Фильтр по рабочей среде """

        if self.ui.checkBox_4.isChecked() == True:
            self.ui.comboBox_3.setDisabled(False)
        else:
            self.ui.comboBox_3.setDisabled(True)

    def setTempretureFrom(self):
        """ Фильтр по т.о.с. (ОТ) """

        if self.ui.checkBox_5.isChecked() == True:
            self.ui.lineEdit_23.setDisabled(False)
        else:
            self.ui.lineEdit_23.setDisabled(True)

    def setTempretureTo(self):
        """ Фильтр по т.о.с. (ДО) """

        if self.ui.checkBox_6.isChecked() == True:
            self.ui.lineEdit_24.setDisabled(False)
        else:
            self.ui.lineEdit_24.setDisabled(True)

    def setTypeConnection(self):
        """ Фильтр по типу присоединения """

        if self.ui.checkBox_7.isChecked() == True:
            self.ui.comboBox_6.setDisabled(False)
        else:
            self.ui.comboBox_6.setDisabled(True)

    def setConnectionSizes(self):
        """ Фильтр по присоединительным размерам """

        if self.ui.checkBox_8.isChecked() == True:
            self.ui.comboBox_17.setDisabled(False)
        else:
            self.ui.comboBox_17.setDisabled(True)

    def setWeight(self):
        """ Фильтр по весу """

        if self.ui.checkBox_9.isChecked() == True:
            self.ui.lineEdit_25.setDisabled(False)
        else:
            self.ui.lineEdit_25.setDisabled(True)

    def changeImage(self):
        """ Изменить или добавить картинку для клапана """

        image, _ = QFileDialog.getOpenFileName(self,
                                               "Вставить новое изображение",
                                               "",
                                               "Image files (*.jpg, *.jpeg, *.jpe, *.jfif, *.png)")
        try:
            file = open(image, 'rb')
            with file:
                data = file.read()
            con = lite.connect(db_)
            with con:
                cur = con.cursor()
                sql = ''' UPDATE valve
                        SET pic = ?
                        WHERE mark = ? '''
                cur.execute(sql, (lite.Binary(data), namedMark))
            con.close()

            QMessageBox.information(self, "Подтверждение",
                                    "Изображение загружено",
                                    QMessageBox.Ok)
        except Exception as e:
            pass

    def openDb(self):
        """ Выбрав файл с БД, функция возвратит путь файла """

        global db_

        try:
            db_, _ = QFileDialog.getOpenFileName(self,
                                                   "Подключиться к БД",
                                                   "",
                                                   "DataBase files (*.db, *.sqlite)")
            self.initRows() # Инициализация пустых записей.
            self.billRows() # Заполнение записей
            self.addItemList() # Заполнение листбокса
            self.comboMaterial() # Заполнение comboBox материалов
            self.comboWorkspace() # Заполнение comboBox окружающей среды
            self.comboTypeConnection() # Заполнение comboBox типа присоединения
            self.comboConnectionSize() # Заполнение comboBox присоединительных размеров
            QMessageBox.information(self, "Готово к работе!",
                                    "База данных загружена.",
                                    QMessageBox.Ok)
        except Exception as e:
            pass

    def createBackUp(self):
        """ Создать бэкап БД """

        print(db_)
        dst_ = db_[0:-11]
        text, ok = QInputDialog.getText(self, 'Back up',
                                        'Введите имя файла бэкапа:');
        if text:
            path = dst_+text+'.sqlite'
            shutil.copy(db_, path)
            QMessageBox.information(self, "Подтверждение",
                                    "Копия создана\nПуть: "+path,
                                    QMessageBox.Ok)


if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())

