import io;
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
        int n = 5;
        int res = factorial(n);
        io.out(res);
        io.out("\n");
    }
}
