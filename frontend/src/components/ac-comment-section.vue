<template>
  <div class="row shadowed comment-section">
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
    <div v-else class="text-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
    <div v-if="growing !== null" v-observe-visibility="moreComments"></div>
    <div v-if="fetching"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
    <ac-new-comment ref="newComment" v-if="(growing !== null && !fetching && !locked)" :parent="this" :url="commenturl"></ac-new-comment>
    <div v-else-if="locked" class="text-center">Comments have been locked.</div>
  </div>
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
    props: ['commenturl', 'nesting', 'parent', 'locked'],
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