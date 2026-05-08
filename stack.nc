// demonstration of a stack in no-c that can be imported into another file
module stack
{
    export { Stack, makeStack }

    type Stack
    {
        mut int[] data;
        mut int top;

        fn void push(int val)
        {
            this.data[this.top] = val;
            this.top++;
        }

        fn int pop()
        {
            if (this.isEmpty())
            {
                raise "pop from empty stack";
            }
            this.top--;
            return this.data[this.top];
        }

        fn int peek()
        {
            if (this.isEmpty())
            {
                raise "peek from empty stack";
            }
            return this.data[(this.top - 1)];
        }

        fn bool isEmpty()
        {
            return (this.top == 0);
        }

        fn int size()
        {
            return this.top;
        }
    }

    fn Stack makeStack()
    {
        return new Stack([], 0);
    }
}
