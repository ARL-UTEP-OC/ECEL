import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gdk
import os
import subprocess
import status_icon
import definitions
import engine.collector
from gui.export_gui import ExportGUI
from gui.progress_bar import ProgressBar
from gui.plugin_config_gui import PluginConfigGUI
from _version import __version__

class MainGUI(Gtk.Window):

    def __init__(self, app_engine):
        super(MainGUI, self).__init__()

        self.set_title("Evaluator-Centric and Extensible Logger v%s" % (__version__))
        self.set_size_request(650, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", self.hide_on_delete)

        self.engine = app_engine

        self.grid = Gtk.Grid()

        self.cssProvider = Gtk.CssProvider()
        self.set_styles()

        self.startall_button = Gtk.ToolButton()
        self.startall_button.set_icon_widget(self.get_image("start.png"))
        self.startall_button.connect("clicked", self.run_collector_actions)

        self.stopall_button = Gtk.ToolButton()
        self.stopall_button.set_icon_widget(self.get_image("stop.png"))
        self.stopall_button.connect("clicked", self.run_collector_actions)

        self.parseall_button = Gtk.ToolButton()
        self.parseall_button.set_icon_widget(self.get_image("json.png"))
        self.parseall_button.connect("clicked", self.run_collector_actions)

        self.export_button = Gtk.ToolButton()
        self.export_button.set_icon_widget(self.get_image("export.png"))
        self.export_button.connect("clicked", self.export_all)

        self.remove_data_button = Gtk.ToolButton(Gtk.Image.new_from_file(os.path.join(definitions.ICONS_DIR, "delete.png")))
        self.remove_data_button.set_icon_widget(self.get_image("delete.png"))
        self.remove_data_button.connect("clicked", self.delete_all)

        self.collector_config_button = Gtk.ToolButton()
        self.collector_config_button.set_icon_widget(self.get_image("settings.png"))
        self.collector_config_button.connect("clicked", self.configure_collectors)

        self.toolbarWidget = Gtk.Box()
        self.toolbarWidget.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.toolbarWidget.set_size_request(650,20)
        self.toolbarWidget.add(self.create_toolbar())

        self.collectorWidget = Gtk.Box()
        self.collectorWidget.set_orientation(Gtk.Orientation.VERTICAL)
        self.collectorWidget.set_size_request(225,480)

        self.pluginWidget = Gtk.Box()
        self.pluginWidget.set_size_request(425,480)

        self.main_body = Gtk.Box()
        self.main_body.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.main_body.add(self.collectorWidget)
        self.main_body.add(self.pluginWidget)

        self.grid.set_orientation(Gtk.Orientation.VERTICAL)
        self.grid.add(self.toolbarWidget)
        self.grid.add(self.main_body)

        self.add(self.grid)

        self.connect("destroy", self.close_all)

        for i, collector in enumerate(self.engine.collectors):
            print "%d) %s" % (i, collector.name)
            self.collectorWidget.pack_start(self.create_collector_frame(collector), True, True, 0)

        self.show_all()
        self.status_context_menu = status_icon.CustomSystemTrayIcon(app_engine, self)

    def create_toolbar(self):
        toolbar = Gtk.Toolbar()
        toolbar.set_style(Gtk.ToolbarStyle.ICONS)

        separator1 = Gtk.SeparatorToolItem()
        separator2 = Gtk.SeparatorToolItem()
        separator3 = Gtk.SeparatorToolItem()

        toolbar.insert(self.startall_button, 0)
        toolbar.insert(separator1, 1)
        toolbar.insert(self.export_button, 2)
        toolbar.insert(separator2,3)
        toolbar.insert(self.remove_data_button, 4)
        toolbar.insert(separator3, 5)
        toolbar.insert(self.collector_config_button, 6)
        toolbar.set_size_request(650,20)

        return toolbar

    def update_collector_action(self, event, collector,action):

        if(action == definitions.Action.RUN):
            collector.set_action(definitions.Action.RUN)
        if(action == definitions.Action.STOP):
            collector.set_action(definitions.Action.STOP)
        if(action == definitions.Action.PARSE):
            collector.set_action(definitions.Action.PARSE)

    def run_collector_actions(self, event):
        for collector in self.engine.collectors:
            action = collector.get_action()
            if collector.is_enabled() and isinstance(collector, engine.collector.AutomaticCollector):
                if(action == definitions.Action.RUN):
                    collector.run()
                if(action == definitions.Action.STOP):
                    collector.terminate()
                if(action == definitions.Action.PARSE):
                    collector.parser.parse()
                if(action == definitions.Action.NOTHING):
                    print("NO action specified for " + collector.name + " collector")

    def get_image(self,name):
        image = Gtk.Image()
        image.set_from_file(os.path.join(definitions.ICONS_DIR, name))
        image.show()
        return image

    def configure_collectors(self, event):
        PluginConfigGUI(self, self.engine.collectors)

    def show_gui(self):
        self.present()
        self.show_all()

    def export_all(self, event):
        ExportGUI(self)

    def delete_all(self, event):
        if self.show_confirmation_dialog("Are you sure you want to delete all collector data (this cannot be undone)?"):
            remove_cmd = os.path.join(os.path.join(os.getcwd(), "scripts"), "cleanCollectorData.sh")
            subprocess.call(remove_cmd) #TODO: Change this to not call external script

    def set_styles(self):
        self.cssProvider.load_from_path("/root/Practicum/ecel/gui/css/widget_styles.css")
        screen = Gdk.Screen.get_default()
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, self.cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def create_collector_frame(self,collector):
        checkBoxWidget = self.create_collector_bbox_widget(collector)
        frame = Gtk.Frame()
        frame.set_label(collector.name)
        frame.add(checkBoxWidget)
        frame.set_size_request(20,20)
        return frame

    def create_collector_bbox_widget(self,collector):
        containerBox = Gtk.ButtonBox()
        containerBox.set_orientation(Gtk.Orientation.VERTICAL)

        checkBoxSection = Gtk.ButtonBox()
        checkBoxSection.set_orientation(Gtk.Orientation.HORIZONTAL)

        runRadio = Gtk.RadioButton("Run")
        runRadio.connect("clicked", self.update_collector_action, collector, definitions.Action.RUN)

        stopRadio = Gtk.RadioButton.new_with_label_from_widget(runRadio, "Stop")
        stopRadio.connect("clicked", self.update_collector_action, collector, definitions.Action.STOP)

        parseRadio = Gtk.RadioButton.new_with_label_from_widget(runRadio, "Parse")
        parseRadio.connect("clicked", self.update_collector_action, collector, definitions.Action.PARSE)

        checkBoxSection.add(runRadio)
        checkBoxSection.add(stopRadio)
        checkBoxSection.add(parseRadio)

        containerBox.add(checkBoxSection)

        return containerBox

    def create_collector_bbox(self, collector):
        frame = Gtk.Frame()

        if collector.is_enabled():
            layout = Gtk.ButtonBoxStyle.SPREAD
            spacing = 10

            bbox = Gtk.HButtonBox()
            bbox.set_border_width(1)
            bbox.set_layout(layout)
            bbox.set_spacing(spacing)
            frame.add(bbox)

            startCollectorButton = Gtk.Button('Start Collector')
            startCollectorButton.connect("clicked", self.startIndividualCollector, collector)
            startCollectorButton.set_sensitive(not isinstance(collector, engine.collector.ManualCollector))
            bbox.add(startCollectorButton)

            stopCollectorButton = Gtk.Button('Stop Collector')
            stopCollectorButton.connect("clicked", self.stopIndividualCollector, collector)
            stopCollectorButton.set_sensitive(not isinstance(collector, engine.collector.ManualCollector))
            bbox.add(stopCollectorButton)

            parseButton = Gtk.Button('Parse Data')
            parseButton.connect("clicked", self.parser, collector)
            bbox.add(parseButton)
        else:
            label = Gtk.Label(label="Collector Disabled")
            frame.add(label)

        return frame

    def startall_collectors(self, button):
        # self.status_context_menu.tray_ind.set_icon(Gtk.STOCK_NO)
        self.status_context_menu.stopall_menu_item.set_sensitive(False)
        self.status_context_menu.startall_menu_item.set_sensitive(True)
        self.stopall_button.set_sensitive(False)
        self.startall_button.set_sensitive(True)
        i = 0.0
        pb = ProgressBar()
        while Gtk.events_pending():
            Gtk.main_iteration()

        for collector in self.engine.collectors:
            if collector.is_enabled() and isinstance(collector, engine.collector.AutomaticCollector):
                collector.run()
            pb.setValue(i / len(self.engine.collectors))
            pb.pbar.set_text("Stopping " + collector.name)
            while Gtk.events_pending():
                Gtk.main_iteration()
            i += 1
            if(i == len(self.engine.collectors)):
                pb.setValue(100)
            pb.destroy()
        #if not pb.emit("delete-event", Gdk.Event(Gdk.DELETE)):
            #pb.destroy()

    def stopall_collectors(self, button):
        # self.status_context_menu.tray_ind.set_icon(Gtk.STOCK_NO)
        self.status_context_menu.stopall_menu_item.set_sensitive(False)
        self.status_context_menu.startall_menu_item.set_sensitive(True)
        self.stopall_button.set_sensitive(False)
        self.startall_button.set_sensitive(True)
        i = 0.0
        pb = ProgressBar()
        while Gtk.events_pending():
            Gtk.main_iteration()

        for collector in self.engine.collectors:
            if collector.is_enabled() and isinstance(collector, engine.collector.AutomaticCollector):
                collector.terminate()
            pb.setValue(i / len(self.engine.collectors))
            pb.pbar.set_text("Stopping " + collector.name)
            while Gtk.events_pending():
                Gtk.main_iteration()
            i += 1
            if (i == len(self.engine.collectors)):
                pb.setValue(100)
            pb.destroy()
            # if not pb.emit("delete-event", Gdk.Event(Gdk.DELETE)):
            # pb.destroy()

    def parse_all(self, event):
        i = 0.0
        pb = ProgressBar()
        while Gtk.events_pending():
            Gtk.main_iteration()

        for collector in self.engine.collectors:
            collector.parser.parse()
            pb.setValue(i/len(self.engine.collectors))
            pb.pbar.set_text("Parsing " + collector.name)
            while Gtk.events_pending():
                Gtk.main_iteration()
            i += 1
        if not pb.emit("delete-event", Gdk.Event(Gdk.DELETE)):
            pb.destroy()

        alert = Gtk.MessageDialog(self, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO,
                                      Gtk.ButtonsType.CLOSE, "Parsing complete")
        alert.run()
        alert.destroy()

    def close_all(self, event):
        for collector in self.engine.collectors:
            if collector.is_enabled:
               collector.terminate()
        os._exit(0)

    def parser(self, event, collector):
        collector.parser.parse()

    def stopIndividualCollector(self, event, collector):
        collector.terminate()

    def startIndividualCollector(self, event, collector):
        collector.run()

    def show_confirmation_dialog(self, msg):
        dialog = Gtk.MessageDialog(self, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO,
                                      Gtk.ButtonsType.YES_NO, msg)
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            return True

        return False
