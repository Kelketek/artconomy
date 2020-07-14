<template>
  <div></div>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {userHandle} from '@/store/profiles/handles'
import {User} from '@/store/profiles/types/User'
import {ProfileController} from '@/store/profiles/controller'

  @Component
export default class UserProp extends Vue {
    public userHandler: ProfileController = null as unknown as ProfileController

    @userHandle('userHandler')
    public subject!: User | null

    @userHandle('undefinedHandler')
    public target!: User | null

    @userHandle('forgettable', false)
    public forgetMe!: User | null

    public created() {
      this.userHandler = this.$getProfile('Fox', {})
      this.userHandler.user.get().then()
    }
}
</script>

<style scoped>

</style>
