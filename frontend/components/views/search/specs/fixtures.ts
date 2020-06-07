export default function searchSchema() {
  return {
    // Endpoint will be ignored here.
    endpoint: '/',
    fields: {
      q: {value: '', omitIf: ''},
      watch_list: {value: null, omitIf: null},
      shield_only: {value: null, omitIf: null},
      featured: {value: null, omitIf: null},
      rating: {value: null, omitIf: null},
      lgbt: {value: null, omitIf: null},
      artists_of_color: {value: null, omitIf: null},
      max_price: {value: '', omitIf: ''},
      min_price: {value: '', omitIf: ''},
    },
  }
}
