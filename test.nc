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
        int[] k = [0, 333, 1];
        Stack s = stack.makeStack(); 
        mut int q = 0;
        q = io.input("enter: ");
        io.outln(q);
        int n = 5;
        int j = n + q;
        io.outln(j);
        int res = factorial(j);
        io.outln(2.23 - 3);
        io.outln(res);
        io.outln(k[1]);
        io.out("\n");
        mut string b = "aads";
       // b[0] = "1";
    }
}
