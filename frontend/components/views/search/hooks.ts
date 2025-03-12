import { useForm } from "@/store/forms/hooks.ts"
import { fallback, fallbackBoolean, searchSchema } from "@/lib/lib.ts"
import { useRoute } from "vue-router"
import { useRegistry } from "@/store/hooks.ts"

export const useSearchForm = () => {
  const formRegistry = useRegistry("Form")
  let populate = true
  if (formRegistry.controllers.search) {
    populate = false
  }
  const form = useForm("search", searchSchema())
  const route = useRoute()
  if (!populate) {
    return form
  }
  const query = { ...route.query }
  form.fields.q.update(fallback(query, "q", ""))
  form.fields.content_ratings.update(fallback(query, "content_ratings", ""))
  form.fields.minimum_content_rating.update(
    fallback(query, "minimum_content_rating", 0),
  )
  form.fields.watch_list.update(fallbackBoolean(query, "watch_list", false))
  form.fields.shield_only.update(fallbackBoolean(query, "shield_only", false))
  form.fields.featured.update(fallbackBoolean(query, "featured", false))
  form.fields.rating.update(fallbackBoolean(query, "rating", false))
  form.fields.commissions.update(fallbackBoolean(query, "commissions", false))
  form.fields.artists_of_color.update(
    fallbackBoolean(query, "artists_of_color", false),
  )
  form.fields.lgbt.update(fallbackBoolean(query, "lgbt", false))
  form.fields.max_price.update(fallback(query, "max_price", ""))
  form.fields.min_price.update(fallback(query, "min_price", ""))
  form.fields.max_turnaround.update(fallback(query, "max_turnaround", ""))
  form.fields.page.update(fallback(query, "page", 1))
  return form
}
