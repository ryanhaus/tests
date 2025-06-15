use minifb::{Key, Window, WindowOptions};

const BUFFER_WIDTH: usize = 160;
const BUFFER_HEIGHT: usize = 144;

const WINDOW_SCALE: usize = 4;
const WINDOW_WIDTH: usize = BUFFER_WIDTH * WINDOW_SCALE;
const WINDOW_HEIGHT: usize = BUFFER_HEIGHT * WINDOW_SCALE;

fn main() {
    let mut buffer: Vec<u32> = vec![0; BUFFER_WIDTH * BUFFER_HEIGHT];

    let mut window = Window::new(
        "Test window",
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        WindowOptions::default(),
    ).unwrap();

    window.set_target_fps(60);

    let colors = [ 0x9BBC0F, 0x8BAC0F, 0x306230, 0x0F380F ];

    while window.is_open() && !window.is_key_down(Key::Escape) {
        for (i, pixel) in buffer.iter_mut().enumerate() {
            let x = i % BUFFER_WIDTH;
            let y = i / BUFFER_WIDTH;

            *pixel = colors[(x+y) % 4];
        }

        window.update_with_buffer(&buffer, BUFFER_WIDTH, BUFFER_HEIGHT).unwrap();
    }
}
