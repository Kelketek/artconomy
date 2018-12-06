<template>
  <div>
    <v-container>
      <v-layout row wrap>
        <v-flex xs12>
          <h1>Ratings for</h1>
          <ac-avatar :user="user" :show-rating="true"></ac-avatar>
        </v-flex>
      </v-layout>
    </v-container>
    <v-container v-if="response">
      <v-card v-for="rating in growing" :key="rating.id" class="mb-2">
        <v-card-text>
          <v-layout row wrap>
            <v-flex xs12 sm2 md1 text-xs-center text-sm-left>
              <ac-avatar :user="rating.rater"></ac-avatar>
            </v-flex>
            <v-flex xs12 sm5 md2 text-xs-center text-sm-left>
              <ac-rating :value="rating.stars"></ac-rating>
            </v-flex>
            <v-flex xs12 sm5 md9 text-xs-center text-sm-left v-if="rating.comments">
              <div v-html="md.render(rating.comments)">
              </div>
            </v-flex>
          </v-layout>
        </v-card-text>
      </v-card>
    </v-container>
    <v-layout row>
      <v-flex xs12 text-xs-center>
        <div v-if="(growing !== null) && furtherPagination" v-observe-visibility="moreRatings"></div>
        <div v-if="fetching"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
  import Paginated from '../mixins/paginated'
  import AcAvatar from './ac-avatar'
  import AcRating from './ac-rating'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import { ObserveVisibility } from 'vue-observe-visibility'
  import { md } from '../lib'

  export default {
    name: 'Ratings',
    components: {AcRating, AcAvatar},
    mixins: [Paginated, Viewer, Perms],
    directives: {'observe-visibility': ObserveVisibility},
    props: ['username'],
    data () {
      return {
        url: `/api/sales/v1/account/${this.username}/ratings/`,
        md
      }
    },
    methods: {
      moreRatings (isVisible) {
        if (isVisible) {
          this.loadMore()
        }
      }
    }
  }
</script>

<style scoped>

</style>