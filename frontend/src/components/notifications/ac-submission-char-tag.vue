<template>
  <div class="row">
    <div class="col-4 col-lg-2" v-if="event.target">
      <router-link :to="{name: 'Submission', params: {assetID: event.target.id}}">
        <ac-asset class="p-2" :terse="true" :asset="event.target" thumb-name="notification" />
      </router-link>
    </div>
    <div class="col-6">
      <div class="p2">
        <p>
            <span v-if="event.data.character">{{event.data.character.name}}</span>
            <span v-else>A removed character</span>
            was tagged in your submission titled '{{event.target.title}}'
          <span v-if="event.data.user">by
            <strong>
              <router-link :to="{name: 'Profile', params: {username: event.data.user.username}}">{{event.data.user.username}}</router-link>.
            </strong>
          </span>
            <span v-else>by a removed user.</span>
        </p>
        <p v-if="event.data.character">
          <router-link :to="{name: 'Character', params: {character: event.data.character.name, username: event.data.character.user.username}}">
            <ac-asset :terse="true" :asset="event.data.character.primary_asset" thumb-name="notification" />
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
  import AcAsset from '../ac-asset'
  import Notification from '../../mixins/notification'

  export default {
    components: {AcAsset},
    name: 'ac-submission-char-tag',
    mixins: [Notification]
  }
</script>