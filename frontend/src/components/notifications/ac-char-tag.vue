<template>
    <div class="row">
      <div class="col-4 col-lg-2" v-if="event.target">
        <router-link v-if="event.data.asset" :to="{name: 'Submission', params: {assetID: event.data.asset.id}}">
          <ac-asset class="p-2" :terse="true" :asset="event.target.primary_asset" thumb-name="notification" />
        </router-link>
        <ac-asset v-else class="p-2" :terse="true" :asset="event.target.primary_asset" thumb-name="notification" />
      </div>
      <div class="col-6">
        <div class="p2">
          <p>
            <strong>
              {{event.target.name}} was tagged in a submission
              <span v-if="event.data.user">by {{event.data.user.username}}</span>
              <span v-else>by a removed user</span>
              <span v-if="event.data.asset">titled '{{event.data.asset.title}}'.</span>
              <span v-else> but the submission was removed.</span>
            </strong>
          </p>
          <p v-if="event.data.asset">
            <router-link :to="{name: 'Submission', params: {assetID: event.data.asset.id}}">
              <ac-asset :terse="true" :asset="event.data.asset" thumb-name="notification" />
            </router-link>
          </p>
        </div>
      </div>
    </div>
</template>

<style scoped>
  .notification-preview {
    width: 80px;
    height: 80px;
  }
</style>

<script>
  import AcAsset from '../ac-asset'

  export default {
    name: 'ac-char-tag',
    props: ['event'],
    components: {
      AcAsset
    }
  }
</script>