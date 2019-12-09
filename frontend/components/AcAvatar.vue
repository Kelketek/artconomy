<template>
  <v-flex shrink text-xs-center class="ac-avatar">
    <v-layout column>
      <v-flex>
        <ac-link :to="profileLink">
          <v-avatar>
            <img alt="" :src="person.avatar_url" v-if="person">
            <v-icon v-else>person</v-icon>
          </v-avatar>
        </ac-link>
      </v-flex>
      <v-flex v-if="showName" class="text-xs-center">
        <v-tooltip bottom v-if="person && person.is_superuser">
          <v-icon slot="activator" small class="green--text">stars</v-icon>
          <span>Admin</span>
        </v-tooltip>
        <v-tooltip bottom v-else-if="person && person.is_staff">
          <v-icon slot="activator" small class="yellow--text">stars</v-icon>
          <span>Staff</span>
        </v-tooltip>
        <ac-link :to="profileLink" v-else>{{ displayName }}</ac-link>
      </v-flex>
      <v-flex v-if="person && removable">
        <v-btn small icon color="danger" @click="$emit('remove')"><v-icon small>close</v-icon></v-btn>
      </v-flex>
      <router-link :to="{name: 'Ratings', params: {username: person.username}}" v-if="showRating && person && person.stars">
        <v-rating dense small half-increments :value="person.stars" color="primary"></v-rating>
      </router-link>
    </v-layout>
  </v-flex>
</template>

<style>
  /*noinspection CssUnusedSymbol*/
  .ac-avatar .v-rating.v-rating--dense .v-icon {
    padding: 0.025rem;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'
import {ProfileController} from '@/store/profiles/controller'
import {userHandle} from '@/store/profiles/handles'
import {User} from '@/store/profiles/types/User'
import {artCall, guestName} from '@/lib'
import {profileRegistry} from '@/store/profiles/registry'
import {TerseUser} from '@/store/profiles/types/TerseUser'
import AcLink from '@/components/wrappers/AcLink.vue'
@Component({
  components: {AcLink},
})
export default class AcAvatar extends Vue {
    // The logic for this module is a bit complex because we don't necessarily want to store the user in Vuex for
    // all of the cases we'll use this. For example, when searching for users, it would be wasteful or incomplete to
    // store the user in Vuex.
    @Prop({default: false})
    public noLink!: boolean
    @Prop({default: ''})
    public username!: string
    @Prop()
    public user!: TerseUser
    @Prop()
    public userId!: number
    @Prop({default: true})
    public showName!: boolean
    @Prop({default: false})
    public showRating!: boolean
    @Prop({default: false})
    public removable!: boolean
    @Prop({default: () => undefined})
    public remove!: () => void

    @userHandle('subjectHandler')
    public subject!: User | null

    public subjectHandler: ProfileController = null as unknown as ProfileController

    public setUser(response: User) {
      this.subjectHandler = this.$getProfile(response.username, {})
      this.subjectHandler.user.setX(response)
    }

    @Watch('username')
    public usernameUpdater(value: string) {
      if (!value) {
        // Can happen on destruction
        return
      }
      profileRegistry.unhook((this as any)._uid, this.subjectHandler)
      this.buildHandler(value)
    }

    public buildHandler(username: string) {
      if (username) {
        this.subjectHandler = this.$getProfile(username, {})
        this.subjectHandler.user.get().then().catch(() => {})
        return
      }
      if (!this.userId) {
        throw Error('No username, no ID. We cannot load an avatar.')
      }
      if (this.$store.getters.idMap[this.userId]) {
        username = this.$store.getters.idMap[this.userId]
        this.subjectHandler = this.$getProfile(username, {})
      } else {
        artCall({url: `/api/profiles/v1/data/user/id/${this.userId}/`, method: 'get'}).then(this.setUser).catch(
          () => {},
        )
      }
    }

    public get profileLink() {
      if (!this.person) {
        return null
      }
      if (this.noLink) {
        return null
      }
      if (guestName(this.person.username)) {
        return null
      }
      if (this.person.artist_mode) {
        return {name: 'Products', params: {username: this.person.username}}
      } else {
        return {name: 'AboutUser', params: {username: this.person.username}}
      }
    }

    public get displayName() {
      if (this.person) {
        return this.person.username
      }
      if (this.username) {
        return this.username
      }
      if (this.userId) {
        return `(User ID #${this.userId})`
      }
      return '(Loading)'
    }

    public get person() {
      return this.user || this.subject
    }

    public created() {
      if (this.user) {
        return
      }
      this.buildHandler(this.username)
    }
}
</script>
