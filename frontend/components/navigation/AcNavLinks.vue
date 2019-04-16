<template>
  <v-list dense style="min-height: 75vh">
    <v-list>
      <v-list-tile @click="$emit('input', false)" :class="{'hidden-lg-and-up': !embedded}">
        <v-list-tile-action>
          <v-icon>close</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Close Menu</v-list-tile-title>
      </v-list-tile>
      <v-list-tile to="/" exact>
        <v-list-tile-action>
          <v-icon>home</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Home</v-list-tile-title>
      </v-list-tile>
      <v-list-tile v-if="!isRegistered" :to="{name: 'SessionSettings'}">
        <v-list-tile-action>
          <v-icon>settings</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Settings</v-list-tile-title>
      </v-list-tile>
      <v-list-tile :to="{name: 'Conversations', params: {username: subject.username}}" v-if="isRegistered">
        <v-list-tile-action>
          <v-icon>email</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Private Messages</v-list-tile-title>
      </v-list-tile>
      <v-list-tile :to="{name: 'SearchProducts'}" @click.capture.stop.prevent="searchOpen">
        <v-list-tile-action class="who-is-open">
          <v-icon>store</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Who's Open?</v-list-tile-title>
      </v-list-tile>
      <v-list-tile :to="{name: 'SearchSubmissions'}" @click.capture.stop.prevent="searchSubmissions">
        <v-list-tile-action class="recent-art">
          <v-icon>photo_library</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Recent Art</v-list-tile-title>
      </v-list-tile>
      <v-list-tile :to="{name: 'CurrentOrders', params: {username: subject.username}}" v-if="isLoggedIn">
        <v-list-tile-action>
          <v-icon>shopping_basket</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Orders</v-list-tile-title>
      </v-list-tile>
      <v-list-tile :to="{name: 'LinksAndStats', params: {username: subject.username}}" v-if="isRegistered">
        <v-list-tile-action>
          <v-icon>star</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>
          Referrals, Rewards, and Tools!
        </v-list-tile-title>
      </v-list-tile>
      <v-list-tile :to="{name: 'Upgrade'}" v-if="isRegistered && !embedded">
        <v-list-tile-action>
          <v-icon>arrow_upward</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>
          Upgrade
        </v-list-tile-title>
      </v-list-tile>
      <v-list-tile class="hidden-sm-and-up" v-if="!embedded && subject && subject.rating > 0">
        <ac-patch-field
            field-type="v-switch"
            :patcher="sfwMode"
            :save-indicator="false"
            label="SFW Mode"
        ></ac-patch-field>
      </v-list-tile>
    </v-list>
    <v-list v-if="isLoggedIn && subject.artist_mode">
      <v-divider></v-divider>
      <v-list-tile :to="{name: 'Store', params: {username: subject.username}}">
        <v-list-tile-action>
          <v-icon>storefront</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>My Store</v-list-tile-title>
      </v-list-tile>
      <v-list-tile :to="{name: 'CurrentSales', params: {username: subject.username}}">
        <v-list-tile-action>
          <v-icon>monetization_on</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Sales</v-list-tile-title>
      </v-list-tile>
      <v-divider></v-divider>
    </v-list>
    <v-list v-if="isStaff">
      <v-list-tile :to="{name: 'Reports'}" v-if="isSuperuser">
        <v-list-tile-action>
          <v-icon>insert_chart</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Reports</v-list-tile-title>
      </v-list-tile>
      <v-list-tile :to="{name: 'CurrentCases', params: {username: subject.username}}">
        <v-list-tile-action>
          <v-icon>gavel</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Cases</v-list-tile-title>
      </v-list-tile>
    </v-list>
    <v-list-group :to="{name: 'Options', params: {'username': subject.username}}" v-if="isRegistered">
      <v-list-tile slot="activator">
        <v-list-tile-action>
          <v-icon>settings</v-icon>
        </v-list-tile-action>
        <v-list-tile-title>Settings</v-list-tile-title>
      </v-list-tile>
      <ac-setting-nav :username="subject.username"></ac-setting-nav>
    </v-list-group>
    <!--        <v-list-tile :to="{name: 'Upgrade'}" v-if="!landscape && isLoggedIn">-->
    <!--          <v-list-tile-action>-->
    <!--            <v-icon>arrow_upward</v-icon>-->
    <!--          </v-list-tile-action>-->
    <!--          <v-list-tile-title>Upgrade!</v-list-tile-title>-->
    <!--        </v-list-tile>-->
    <v-list-tile :to="{name: 'About'}" v-if="!embedded">
      <v-list-tile-action>
        <v-icon>question_answer</v-icon>
      </v-list-tile-action>
      <v-list-tile-title>FAQ</v-list-tile-title>
    </v-list-tile>
    <v-list-tile @click.prevent="logout()" v-if="isRegistered && !embedded">
      <v-list-tile-action class="logout-button">
        <v-icon>exit_to_app</v-icon>
      </v-list-tile-action>
      <v-list-tile-title>Log out</v-list-tile-title>
    </v-list-tile>
    <v-list-tile class="mt-3" :to="{name: 'Policies'}" v-if="!embedded">
      <v-list-tile-action>
        <v-icon>info</v-icon>
      </v-list-tile-action>
      <v-list-tile-title>Privacy and Legal</v-list-tile-title>
    </v-list-tile>
  </v-list>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import {FormController} from '@/store/forms/form-controller'
import {ProfileController} from '@/store/profiles/controller'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {artCall} from '@/lib'
  @Component({
    components: {AcPatchField, AcSettingNav},
  })
export default class AcNavDrawer extends Vue {
    public searchForm: FormController = null as unknown as FormController
    @Prop({required: true})
    public value!: boolean
    @Prop({required: true})
    public subjectHandler!: ProfileController
    @Prop({required: true})
    public isRegistered!: boolean
    @Prop({required: true})
    public isLoggedIn!: boolean
    @Prop({default: false})
    public embedded!: boolean
    @Prop({required: true})
    public isStaff!: boolean
    @Prop({required: true})
    public isSuperuser!: boolean

    public get subject() {
      return this.subjectHandler.user.x
    }

    public get sfwMode() {
      return this.subjectHandler.user.patchers.sfw_mode
    }

    public searchOpen() {
      this.searchForm.reset()
      this.$router.push({name: 'SearchProducts'})
    }

    public searchSubmissions() {
      this.searchForm.reset()
      this.$router.push({name: 'SearchSubmissions'})
    }

    public logout() {
      artCall({
        url: '/api/profiles/v1/logout/',
        method: 'post',
      }).then(this.subjectHandler.user.setX).then(() => {
        this.$router.push({name: 'Home'})
        this.$emit('input', null)
      })
    }

    public created() {
      this.searchForm = this.$getForm('search')
    }
}
</script>
