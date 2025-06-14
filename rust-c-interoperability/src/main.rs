mod test_bindings;

fn main() {
    let result = unsafe { test_bindings::test(5, 3) };
    println!("Result: {result}");
}
