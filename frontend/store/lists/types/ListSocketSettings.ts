import ListSocketSpec from '@/store/lists/types/ListSocketSpec'

export interface ListSocketSettings {
    appLabel: string,
    modelName: string,
    keyField?: string,
    serializer: string,
    list: ListSocketSpec,
}
