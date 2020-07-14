<template>
  <div class="ac-avatar shrink text-center flex">
    <div class="flex">
      <div class="flex">
        <ac-link :to="profileLink">
          <v-avatar>
            <img alt="" :src="person.avatar_url" v-if="person">
            <v-icon v-else>person</v-icon>
          </v-avatar>
        </ac-link>
      </div>
      <div v-if="showName" class="text-center flex">
        <v-tooltip bottom v-if="person && person.is_superuser">
          <template v-slot:activator="{on}">
            <v-icon small class="green--text" v-on="on">stars</v-icon>&nbsp;
          </template>
          <span>Admin</span>
        </v-tooltip>
        <v-tooltip bottom v-else-if="person && person.is_staff">
          <template v-slot:activator="{on}">
            <v-icon v-on="on" small class="yellow--text">stars</v-icon>&nbsp;
          </template>
          <span>Staff</span>
        </v-tooltip>
        <ac-link :to="profileLink">{{ displayName }}</ac-link>
      </div>
      <div v-if="person && removable" class="flex">
        <v-btn small icon color="danger" @click="$emit('remove')"><v-icon small>close</v-icon></v-btn>
      </div>
      <router-link :to="{name: 'Ratings', params: {username: person.username}}" v-if="showRating && person && person.stars">
        <v-rating dense small half-increments :value="person.stars" color="primary" />
      </router-link>
    </div>
  </div>
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
import {artCall, profileLink} from '@/lib/lib'
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
      if (this.noLink) {
        return null
      }
      return profileLink(this.person)
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
