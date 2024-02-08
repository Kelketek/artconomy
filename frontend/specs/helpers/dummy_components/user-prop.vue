<template>
  <div></div>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import {userHandle} from '@/store/profiles/handles.ts'
import {User} from '@/store/profiles/types/User.ts'
import {ProfileController} from '@/store/profiles/controller.ts'
import {ArtVue} from '@/lib/lib.ts'

@Component
class UserProp extends ArtVue {
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
export default toNative(UserProp)
</script>

<style scoped>

</style>
