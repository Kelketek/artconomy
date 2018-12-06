<template>
  <v-container fluid>
    <ac-comment
        v-for="comment in growing"
        :commentobj="comment"
        :key="comment.id"
        :reader="$root.user"
        v-if="growing !== null"
        :nesting="nesting"
        :toplevel="true"
        :locked="locked"
    >

    </ac-comment>
    <v-layout v-else row wrap>
      <v-flex xs12 class="text-xs-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></v-flex>
    </v-layout>
    <v-layout row wrap>
      <v-flex xs12 v-if="growing !== null" v-observe-visibility="moreComments">&nbsp</v-flex>
      <v-flex xs12 v-if="fetching" text-xs-center><i class="fa fa-spin fa-spinner fa-5x"></i></v-flex>
    </v-layout>
    <ac-new-comment ref="newComment" v-if="(growing !== null && !fetching && !locked)" :parent="this" :url="commenturl" />
    <v-layout v-else-if="locked" row wrap>
      <v-flex xs12 class="col-12 text-section text-xs-center">Comments have been locked.</v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import AcComment from './ac-comment'
  import AcNewComment from './ac-new-comment'
  import Paginated from '../mixins/paginated'
  import { ObserveVisibility } from 'vue-observe-visibility'
  import { artCall } from '../lib'

  export default {
    name: 'ac-comment-section',
    components: {AcComment, AcNewComment},
    props: {commenturl: {}, nesting: {}, parent: {}, locked: {}, autoFetch: {default: false}},
    directives: {'observe-visibility': ObserveVisibility},
    mixins: [Paginated],
    methods: {
      populateComments (response) {
        this.response = response
        this.growing = response.results
      },
      addComment (comment) {
        this.growing.push(comment)
      },
      moreComments (isVisible) {
        if (isVisible) {
          this.loadMore()
        }
      }
    },
    created () {
      artCall(this.commenturl, 'GET', undefined, this.populateComments)
    }
  }
</script>