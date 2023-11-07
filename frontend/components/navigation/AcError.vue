<template>
  <!--suppress JSUnresolvedVariable -->
  <div v-if="code" class="container error-container">
    <div class="row">
      <div class="col-12 text-center">
        <!--suppress JSUnresolvedVariable -->
        <img class="error-logo" :src="logo" :alt="`Error code ${code}`"/>
      </div>
      <div class="col-12 text-center home-title">
        <h1>Whoops!</h1>
        <!--suppress JSUnresolvedVariable -->
        <p v-if="code === 500">
          Something went wrong. We've notified our developers and will get it fixed as soon as we can!
        </p>
        <!--suppress JSUnresolvedVariable -->
        <p v-else-if="code === 503">
          Artconomy is currently updating or under maintenance. Please refresh in a few minutes and try again!
        </p>
        <!--suppress JSUnresolvedVariable -->
        <p v-else-if="code === 400">
          Something seems wrong with your request. Could you check the URL?
        </p>
        <!--suppress JSUnresolvedVariable -->
        <p v-else-if="code === 404">
          We couldn't find that page. It might not exist or you might not have the right privileges to see it.
        </p>
        <!--suppress JSUnresolvedVariable -->
        <p v-else-if="code === 403">
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
import {Component, toNative, Vue, Watch} from 'vue-facing-decorator'
import {ArtVue, setMetaContent} from '../../lib/lib'

@Component
class AcErrors extends ArtVue {
  @Watch('$store.state.errors.code')
  private updateMetaError(val: number) {
    if (val) {
      setMetaContent('prerender-status-code', val + '')
    }
  }

  public get code(): number | string {
    return this.$store.state.errors!.code
  }

  public get logo(): string {
    const errors: Array<string|number> = [500, 503, 400, 404, 403]
    if (errors.indexOf(this.code) !== -1) {
      return `/static/images/${this.code}.png`
    } else {
      return '/static/images/generic-error.png'
    }
  }
}

export default toNative(AcErrors)
</script>

<style scoped>
.error-logo {
  width: 25%;
  margin-bottom: 2rem;
}
</style>
