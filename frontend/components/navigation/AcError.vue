<template>
  <!--suppress JSUnresolvedVariable -->
  <div v-if="errors.code" class="container error-container">
    <div class="row">
      <div class="col-12 text-center">
        <!--suppress JSUnresolvedVariable -->
        <img class="error-logo" :src="errorLogo" :alt="`Error code ${errors.code}`"/>
      </div>
      <div class="col-12 text-center home-title">
        <h1>Whoops!</h1>
        <!--suppress JSUnresolvedVariable -->
        <p v-if="errors.code === 500">
          Something went wrong. We've notified our developers and will get it fixed as soon as we can!
        </p>
        <!--suppress JSUnresolvedVariable -->
        <p v-else-if="errors.code === 503">
          Artconomy is currently updating or under maintenance. Please refresh in a few minutes and try again!
        </p>
        <!--suppress JSUnresolvedVariable -->
        <p v-else-if="errors.code === 400">
          Something seems wrong with your request. Could you check the URL?
        </p>
        <!--suppress JSUnresolvedVariable -->
        <p v-else-if="errors.code === 404">
          We couldn't find that page. It might not exist or you might not have the right privileges to see it.
        </p>
        <!--suppress JSUnresolvedVariable -->
        <p v-else-if="errors.code === 403">
          Access to this page is restricted. Please make sure you're logged into an account that has access to it.
        </p>
        <p v-else>
          Something weird happened. Could you please contact support and tell us about it?
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Component from 'vue-class-component'
import Vue from 'vue'
import {Getter, State} from 'vuex-class'
import {ErrorState} from '../../store/errors/types'
import {setMetaContent} from '../../lib'
import {Watch} from 'vue-property-decorator'

  @Component
export default class AcErrors extends Vue {
    @State('errors') public errors!: ErrorState
    @Getter('logo', {namespace: 'errors'}) public errorLogo!: string

    @Watch('errors.code')
    private updateMetaError(val: number) {
      if (val) {
        setMetaContent('prerender-status-code', val + '')
      }
    }
}
</script>

<style scoped>
  .error-logo {
    width: 25%;
    margin-bottom: 2rem;
  }
</style>
