import { FormController } from "@/store/forms/form-controller.ts"
import { useSearchField } from "@/components/views/search/mixins/SearchField.ts"
import { ListController } from "@/store/lists/controller.ts"

export const useSearchList = (
  searchForm: FormController,
  list: ListController<any>,
) => {
  const searchFieldFuncs = useSearchField(searchForm, list)
  searchFieldFuncs.rawUpdate(searchForm.rawData)
  return searchFieldFuncs
}
