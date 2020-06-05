def compress(string):
    new_string = ""
    l = len(string)
    ind = []
    old_c = ""
    print(l)
    for i in range(len(string)):
        if 2*len(ind)>l:
            print("ok")
            return string
        if string[i] == old_c:
            continue
        else:
            old_c = string[i]
            ind.append(i)
        print()
    ind.append(len(string))
    for i in range(len(ind) - 1):
        new_string += (string[ind[i]] + str(ind[i + 1] - ind[i]))

    if len(new_string)>len(string):
        return string
    else:
        return new_string

print(compress("abc"))


print(sorted(zip([4,2,3],[3,4,5])))