import os
from io import BytesIO

# 强制限制与修正移动端环境
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.core.image import Image as KivyCoreImage
from kivy.clock import Clock
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.boxlayout import MDBoxLayout
from plyer import filechooser

# 载入自定义三大依赖模块
from config import AppConfig
from unity_core import UnityBackendCore
from android_bridge import AndroidBridge

class SetupScreen(Screen):
    def save_and_continue(self):
        in_d = self.ids.in_input.text.strip()
        out_d = self.ids.out_input.text.strip()
        if in_d and out_d:
            success, msg = MDApp.get_running_app().app_config.save_paths(in_d, out_d)
            if success:
                MDApp.get_running_app().root.current = 'main'
                MDApp.get_running_app().main_screen.refresh_in_dir()
            else:
                MDApp.get_running_app().show_alert("配置失败", msg)

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.only_tex = True
        self.search_text = ""

    def refresh_in_dir(self):
        """三、显示并刷新 in 文件夹内容，不依赖扩展名"""
        in_dir, _ = MDApp.get_running_app().app_config.get_paths()
        if not in_dir or not os.path.exists(in_dir):
            return
            
        self.ids.view_manager.current = 'file_list_mode'
        container = self.ids.file_container
        container.clear_widgets()
        
        try:
            files = os.listdir(in_dir)
            # 支持列表排序
            files.sort()
            for f in files:
                f_path = os.path.join(in_dir, f)
                if os.path.isfile(f_path):
                    item = OneLineAvatarIconListItem(text=f)
                    item.add_widget(IconLeftWidget(icon="file-document"))
                    item.bind(on_release=lambda x, p=f_path: self.open_unity_file(p))
                    container.add_widget(item)
        except Exception as e:
            MDApp.get_running_app().show_alert("读取失败", str(e))

    def open_unity_file(self, filepath):
        """四、后台线程异步解析 Unity 资源文件，前台同步投递进度"""
        app = MDApp.get_running_app()
        app.show_progress_dialog("正在解包资产...")
        
        def on_progress(percentage, status_text):
            Clock.schedule_once(lambda dt: app.update_progress(percentage, status_text))
            
        def on_finish(success, result):
            Clock.schedule_once(lambda dt: app.close_progress_dialog())
            if success:
                Clock.schedule_once(lambda dt: self.populate_textures())
            else:
                Clock.schedule_once(lambda dt: app.show_alert("解析错误", result))
                
        app.core.async_load_resource(filepath, on_progress, on_finish)

    def populate_textures(self):
        """加载贴图列表视图"""
        self.ids.view_manager.current = 'texture_list_mode'
        container = self.ids.texture_container
        container.clear_widgets()
        
        core = MDApp.get_running_app().core
        names = core.filter_texture_list(only_tex=self.only_tex, search_query=self.search_text)
        
        for name in names:
            meta = core.get_texture_metadata(name)
            res_str = f" [{meta['width']}x{meta['height']}]" if meta else ""
            item = OneLineAvatarIconListItem(text=f"{name}{res_str}")
            item.add_widget(IconLeftWidget(icon="image"))
            item.bind(on_release=lambda x, n=name: self.go_to_detail(n))
            container.add_widget(item)

    def toggle_filter(self):
        self.only_tex = not self.only_tex
        self.ids.filter_btn.text = "✓ 仅显示_tex" if self.only_tex else "显示全部"
        self.populate_textures()

    def on_search(self, text):
        self.search_text = text
        self.populate_textures()

    def go_to_detail(self, texture_name):
        app = MDApp.get_running_app()
        app.detail_screen.load_texture_detail(texture_name)
        app.root.current = 'detail'

    def go_to_settings(self):
        MDApp.get_running_app().root.current = 'setup'

class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tex_name = None

    def load_texture_detail(self, name):
        """七、详情页高清无损预览加载转换"""
        self.tex_name = name
        core = MDApp.get_running_app().core
        meta = core.get_texture_metadata(name)
        
        if meta:
            self.ids.lbl_name.text = f"贴图名称: {meta['name']}"
            self.ids.lbl_res.text = f"分辨率: {meta['width']} x {meta['height']}"
            self.ids.lbl_fmt.text = f"纹理格式: {meta['format']}"
            self.ids.lbl_mip.text = f"是否生成 MipMap: {'是' if meta['mipmap'] else '否'}"
            
        pil_img = core.get_pil_image(name)
        if pil_img:
            # 转换至 Kivy 内部纹理链
            buf = BytesIO()
            pil_img.save(buf, format="PNG")
            buf.seek(0)
            self.ids.image_view.texture = KivyCoreImage(buf, ext="png").texture
            # 重置 Scatter 缩放比例
            self.ids.scatter_container.scale = 1.0
            self.ids.scatter_container.pos = (0, 0)

    def export_to_gallery(self):
        core = MDApp.get_running_app().core
        pil_img = core.get_pil_image(self.tex_name)
        if pil_img:
            success, msg = AndroidBridge.save_to_gallery(pil_img, self.tex_name)
            MDApp.get_running_app().show_alert("导出结果", msg)

    def replace_texture(self):
        """九、调用系统图片选择器完成实时非全局级解包替换"""
        filechooser.open_file(on_selection=self.on_image_picked, title="选择外部替换图片")

    def on_image_picked(self, selection):
        if not selection: return
        img_p = selection[0]
        core = MDApp.get_running_app().core
        
        try:
            from PIL import Image as PILImage
            new_pil = PILImage.open(img_p)
            obj = core.all_textures.get(self.tex_name)
            data = obj.read()
            
            if hasattr(data, 'set_image'):
                data.set_image(new_pil)
            else:
                data.image = new_pil
            data.save()
            
            # 重新刷新当前视图预览
            self.load_texture_detail(self.tex_name)
            MDApp.get_running_app().show_alert("提示", "当前内存纹理已覆写，请点击【保存修改】持久化写出。")
        except Exception as e:
            MDApp.get_running_app().show_alert("替换失败", str(e))

    def save_asset_out(self):
        app = MDApp.get_running_app()
        _, out_dir = app.app_config.get_paths()
        
        app.show_progress_dialog("正在写出重构后的 Unity 资产...")
        
        def on_progress(p, txt):
            Clock.schedule_once(lambda dt: app.update_progress(p, txt))
        def on_finish(success, path_or_err):
            Clock.schedule_once(lambda dt: app.close_progress_dialog())
            if success:
                Clock.schedule_once(lambda dt: app.show_alert("保存成功", f"资产已安全输出至:\n{path_or_err}"))
            else:
                Clock.schedule_once(lambda dt: app.show_alert("保存失败", path_or_err))
                
        app.core.async_save_resource(out_dir, on_progress, on_finish)

    def go_back(self):
        MDApp.get_running_app().root.current = 'main'


class TextureToolApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        # 实例化后台控制核心与配置核心
        self.app_config = AppConfig()
        self.core = UnityBackendCore()
        
        # 实例化页面，注入全局变量
        self.main_screen = MainScreen()
        self.detail_screen = DetailScreen()
        self.setup_screen = SetupScreen()
        
        # 配置路由（与 kv 文件中的 FadeTransition 保持一致）
        from kivy.uix.screenmanager import ScreenManager, FadeTransition
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(self.setup_screen)
        sm.add_widget(self.main_screen)
        sm.add_widget(self.detail_screen)
        
        # 首次启动引导判断
        if self.app_config.is_first_run():
            sm.current = 'setup'
        else:
            sm.current = 'main'
            Clock.schedule_once(lambda dt: self.main_screen.refresh_in_dir(), 0.5)
            
        self.dialog = None
        self.progress_bar = None
        return sm

    # ———————————————————— 进度条与状态公共控制组件 ————————————————————
    def show_progress_dialog(self, text):
        if not self.dialog:
            self.progress_bar = MDProgressBar(value=0, max=100, size_hint_y=None, height=dp(8))
            self.dialog = MDDialog(
                title=text,
                type="custom",
                content_cls=MDBoxLayout(self.progress_bar, orientation="vertical", height=dp(40), size_hint_y=None),
                auto_dismiss=False
            )
        self.dialog.title = text
        self.progress_bar.value = 0
        self.dialog.open()

    def update_progress(self, percentage, text):
        if self.progress_bar:
            self.progress_bar.value = percentage * 100
        if self.dialog:
            self.dialog.title = text

    def close_progress_dialog(self):
        if self.dialog:
            self.dialog.dismiss()

    def show_alert(self, title, text):
        """十三、全局标准异常阻断弹窗，禁止程序直接闪退"""
        d = MDDialog(title=title, text=text, size_hint=(0.8, None))
        d.open()

if __name__ == '__main__':
    TextureToolApp().run()