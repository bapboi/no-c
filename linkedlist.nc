// demonstration of a linked list in no-c

import io;

module main
{
    export { main }

    type Node
    {
        mut int value;
        mut Node next;

        fn int getValue()
        {
            return this.value;
        }

        fn Node getNext()
        {
            return this.next;
        }

        fn void setNext(Node n)
        {
            this.next = n;
        }
    }

    type LinkedList
    {
        mut Node head;
        mut int size;

        fn void push(int value)
        {
            Node n = new Node(value, null);
            n.setNext(this.head);
            this.head = n;
            this.size = (this.size + 1);
        }

        fn void append(int value)
        {
            Node n = new Node(value, null);
            this.size = (this.size + 1);
            if (this.head == null)
            {
                this.head = n;
                return;
            }
            mut Node cur = this.head;
            while (cur.getNext() != null)
            {
                cur = cur.getNext();
            }
            cur.setNext(n);
        }

        fn int pop()
        {
            if (this.head == null)
            {
                return -1;
            }
            int val = this.head.getValue();
            this.head = this.head.getNext();
            this.size = (this.size - 1);
            return val;
        }

        fn void print()
        {
            mut Node cur = this.head;
            io.out("[");
            mut bool first = true;
            while (cur != null)
            {
                if (!first)
                {
                    io.out(", ");
                }
                io.out(cur.getValue());
                first = false;
                cur = cur.getNext();
            }
            io.outln("]");
        }

        fn int length()
        {
            return this.size;
        }
    }

    fn void main()
    {
        LinkedList list = new LinkedList(null, 0);

        list.append(1);
        list.append(2);
        list.append(3);
        list.push(0);

        io.out("list: ");
        list.print();

        io.out("length: ");
        io.outln(list.length());

        int popped = list.pop();
        io.out("popped: ");
        io.outln(popped);

        io.out("list after pop: ");
        list.print();
    }
}
