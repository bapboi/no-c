// test file that includes random operations
import io;
import stack;
module main
{
    export { main }
    fn int factorial(int n)
    {
        if (n <= 1)
        {
            return 1;
        }
        return (n * factorial((n - 1)));
    }
    fn void main()
    {
        Stack s = stack.makeStack(); 
        s.push(3);
        s.push(6);
        s.push(5);
        s.push(1);
        io.out(s.pop());
        io.outln();
        io.out(s.peek());
        io.outln();
        int n = 5;
        int res = factorial(5);
        io.outln(res);
        io.outln(s.pop());

    
        io.outln(s.pop());
        io.outln(s.pop());
    }
}
