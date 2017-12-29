<template>
  <div>
    <div v-if="order" class="container">
      <div class="row shadowed">
        <div class="col-lg-4 col-sm-12 col-md-6 text-section text-center">
          <ac-asset :asset="order.product" thumb-name="preview" img-class="bound-image"></ac-asset>
        </div>
        <div class="col-md-6 col-sm-12 text-section pt-3">
          <h1>{{order.product.name}}</h1>
          <h2>Order #{{order.id}}</h2>
          <div>{{order.product.description}}</div>
          <div class="text-center">
            <h3>Ordered By</h3>
            <ac-avatar :user="order.buyer"></ac-avatar>
          </div>
          <div>
            <h4>Details:</h4>
            {{order.details}}
          </div>
        </div>
        <div class="col-md-6 col-sm-12 col-lg-2 text-section text-center pt-3">
          <h4>Seller:</h4>
          <div class="avatar-container">
            <ac-avatar :user="order.seller"></ac-avatar>
          </div>
          <div class="extra-details">
            <div class="full-width">
              <strong class="day-count"><ac-patchfield v-model="order.product.expected_turnaround" name="expected_turnaround" styleclass="day-count"></ac-patchfield></strong> days
              turnaround
            </div>
            <div class="full-width">
              <strong><ac-patchfield styleclass="revision-count" v-model="order.product.revisions" name="revisions" :editmode="false"></ac-patchfield></strong> included revision<span v-if="order.product.revisions > 1">s</span>
            </div>
          </div>
          <div class="price-container">
            Starting at
            <div class="price-highlight">
              <sup class="mini-dollar">$</sup><ac-patchfield v-model="order.product.price" name="price" :editmode="false"></ac-patchfield>
            </div>
          </div>
        </div>
        <div class="col-sm-12 text-section mb-2">
          <h2>Characters</h2>
        </div>
        <ac-character-preview
            v-for="char in order.characters"
            v-bind:character="char"
            v-bind:expanded="true"
            v-bind:key="char.id"
        >
        </ac-character-preview>
      </div>
      <div class="mb-5">
        <ac-comment-section :commenturl="commenturl" :nesting="false"></ac-comment-section>
      </div>
    </div>
    <div class="row" v-else>
      <div class="text-center" style="width:100%"><i class="fa fa-spin fa-spinner fa-5x"></i></div>
    </div>
  </div>
</template>

<script>
  import AcCharacterPreview from './ac-character-preview'
  import AcCommentSection from './ac-comment-section'
  import AcAvatar from './ac-avatar'
  import AcPatchfield from './ac-patchfield'
  import AcAsset from './ac-asset'
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import { artCall } from '../lib'

  export default {
    props: ['orderID'],
    components: {AcCharacterPreview, AcAvatar, AcPatchfield, AcAsset, AcCommentSection},
    mixins: [Viewer, Perms],
    methods: {
      populateOrder (response) {
        this.order = response
      },
      goToProfile () {
        this.$router.push({name: 'Profile', params: {username: this.viewer.username}})
      }
    },
    data () {
      return {
        order: null,
        commenturl: `/api/sales/v1/order/${this.orderID}/comments/`
      }
    },
    created () {
      artCall(`/api/sales/v1/order/${this.orderID}/`, 'GET', undefined, this.populateOrder)
    }
  }
</script>

<style scoped>
   .v-align-middle {
     vertical-align: middle;
   }
</style>