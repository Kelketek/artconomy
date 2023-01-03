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
      commissions: {value: false, omitIf: false},
      lgbt: {value: null, omitIf: null},
      artists_of_color: {value: null, omitIf: null},
      content_ratings: {value: '', omitIf: ''},
      minimum_content_rating: {value: 0, omitIf: 0},
      max_price: {value: '', omitIf: ''},
      min_price: {value: '', omitIf: ''},
      max_turnaround: {value: '', omitIf: ''},
      size: {value: 24},
      page: {value: 1},
    },
  }
}
