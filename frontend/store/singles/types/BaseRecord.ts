export type BaseRecord<T> ={
    [Property in keyof T as string]: T[Property];
}
