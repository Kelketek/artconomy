<template>
  <div class="notifications-center row">
    <div v-if="response !== null && !growing.length" class="col-sm-12 text-center"><p>You do not have any notifications at this time.</p></div>
    <div class="col-sm-12 text-center">
      <div v-if="growing !== null" v-observe-visibility="moreNotifications"></div>
      <div v-if="fetching"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
    </div>
  </div>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import { artCall } from '../lib'
  import { ObserveVisibility } from 'vue-observe-visibility'

  export default {
    name: 'NotificationCenter',
    mixins: [Paginated],
    directives: {'observe-visibility': ObserveVisibility},
    methods: {
      moreNotifications (isVisible) {
        if (isVisible) {
          this.loadMore()
        }
      },
      populateNotifications (response) {
        this.response = response
        this.growing = response.results
        this.fetching = false
      }
    },
    created () {
      this.fetching = true
      artCall('/api/profiles/v1/data/notifications/', 'GET', undefined, this.populateNotifications, this.$error)
    }
  }
</script>