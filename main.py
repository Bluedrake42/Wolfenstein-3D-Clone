import sys
import pygame as pg
import moderngl as mgl
from engine import Engine
from settings import *
from array import array


class Game:
    def __init__(self):
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, MAJOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, MINOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, DEPTH_SIZE)

        self.screen = pg.display.set_mode(WIN_RES, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.BLEND)
        self.ctx.gc_mode = 'auto'

        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.time = 0

        self.is_running = True
        self.fps_value = 0
        
        # Initialize engine first
        self.engine = Engine(self)
        
        # Show menu and start selected level
        self.show_level_menu()

        self.anim_trigger = False
        self.anim_event = pg.USEREVENT + 0
        pg.time.set_timer(self.anim_event, SYNC_PULSE)

        self.sound_trigger = False
        self.sound_event = pg.USEREVENT + 1
        pg.time.set_timer(self.sound_event, 750)

    def show_level_menu(self):
        # Menu options
        levels = ["Testing Level", "Level 0", "Level 1"]
        selected = 0
        
        # Create a temporary surface for text rendering
        text_surface = pg.Surface((int(WIN_RES.x), int(WIN_RES.y)), pg.SRCALPHA)
        font = pg.font.Font(None, 74)
        
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        
        menu_active = True
        while menu_active:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        selected = (selected - 1) % len(levels)
                    elif event.key == pg.K_DOWN:
                        selected = (selected + 1) % len(levels)
                    elif event.key == pg.K_RETURN:
                        menu_active = False
                        self.engine.player_attribs.num_level = selected
                        self.engine.new_game()
            
            # Clear screen
            self.ctx.clear(color=BG_COLOR)
            
            # Clear text surface
            text_surface.fill((0, 0, 0, 0))
            
            # Render menu options
            for i, text in enumerate(levels):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                text_surface_temp = font.render(text, True, color)
                x = int(WIN_RES.x) // 2 - text_surface_temp.get_width() // 2
                y = int(WIN_RES.y) // 2 - len(levels) * 40 + i * 80
                text_surface.blit(text_surface_temp, (x, y))
            
            # Convert surface to string buffer
            text_data = pg.image.tostring(text_surface, 'RGBA')
            
            # Create texture with integer dimensions
            texture = self.ctx.texture((int(WIN_RES.x), int(WIN_RES.y)), 4, text_data)
            texture.use(0)
            
            # Create simple fullscreen quad program for menu
            program = self.ctx.program(
                vertex_shader='''
                    #version 330
                    in vec2 in_position;
                    in vec2 in_texcoord;
                    out vec2 uv;
                    void main() {
                        gl_Position = vec4(in_position, 0.0, 1.0);
                        uv = in_texcoord;
                    }
                ''',
                fragment_shader='''
                    #version 330
                    uniform sampler2D tex;
                    in vec2 uv;
                    out vec4 color;
                    void main() {
                        color = texture(tex, uv);
                    }
                '''
            )
            
            # Create fullscreen quad
            vertices = [
                -1.0, -1.0, 0.0, 1.0,
                 1.0, -1.0, 1.0, 1.0,
                 1.0,  1.0, 1.0, 0.0,
                -1.0,  1.0, 0.0, 0.0,
            ]
            indices = [0, 1, 2, 0, 2, 3]
            
            vbo = self.ctx.buffer(data=array('f', vertices))
            ibo = self.ctx.buffer(data=array('I', indices))
            
            vao = self.ctx.vertex_array(
                program,
                [
                    (vbo, '2f 2f', 'in_position', 'in_texcoord'),
                ],
                ibo
            )
            
            # Render menu
            vao.render()
            pg.display.flip()
            
            self.clock.tick(60)
            
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

    def update(self):
        self.engine.update()
        #
        self.delta_time = self.clock.tick()
        self.time = pg.time.get_ticks() * 0.001
        self.fps_value = int(self.clock.get_fps())
        pg.display.set_caption(f'{self.fps_value}')

    def render(self):
        self.ctx.clear(color=BG_COLOR)
        self.engine.render()
        pg.display.flip()

    def handle_events(self):
        self.anim_trigger, self.sound_trigger = False, False

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.is_running = False
            #
            if event.type == self.anim_event:
                self.anim_trigger = True
            #
            if event.type == self.sound_event:
                self.sound_trigger = True
            #
            self.engine.handle_events(event=event)

    def run(self):
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()
        pg.quit()
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
