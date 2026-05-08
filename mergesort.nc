import io; 
module main
{
  export { main }

  fn void main()
  {
   
    mut int[] l1 = [0, 2, 1, 6, 3, 9, 4];
    mut int[] l2 = [3, 4, 1, 2, 7, 5, 4];
    io.out("array before mergesort: ");
    io.outln(l1);
    io.outln();
    io.outln("array in the middle of mergesort: ");
    sort(l1, 0, 6);
    io.outln();
    
    io.out("array after mergesort: ");
    io.outln(l1);
  }
  fn void sort(mut int[] arr, int l, int r)
  {
    if (!(l >= r))
    {
    
    
    int m = l + (r - l) / 2;
    sort(arr, l, m);
    sort(arr, m + 1, r);

    merge(arr, l, m, r);
    }
  }
  fn void merge(mut int[] arr, int l, int m, int r)
  {
    int n1 = m - l + 1;
    int n2 = r - m;
    mut int[] result1 = [];
    mut int[] result2 = [];
    for (int q = 0; q < n1; q++)
    {
      result1[q] = arr[l + q];
    }
    for (mut int h = 0; h < n2; h++)
    {
      result2[h] = arr[m + 1 + h];
    }
    mut int i = 0;
    mut int j = 0;
    mut int k = l;
    while ((i < n1) && (j < n2))
    {
      io.outln(arr);
      if (result1[i] <= result2[j])
      {
        arr[k] = result2[j];
        j++;
      }
      else 
      {
        arr[k] = result1[i];
        i++;
      }
      k++;
    }
    while (i < n1)
    {
      arr[k] = result1[i];
      i++;
      k++;
    }
    while (j < n2)
    {
      arr[k] = result2[j];
      j++;
      k++;
    }
     
  }

}
